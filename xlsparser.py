# -*- coding: utf-8 -*-

import traceback
import numfmt
import xlsconfig
from tps import tp0

def format_number_with_xlrd(f, cell, wb):
	xf = wb.xf_list[cell.xf_index]
	fmt_key = xf.format_key
	fmt = wb.format_map[fmt_key]
	s_fmt = fmt.format_str
	a_fmt = numfmt.extract_number_format(s_fmt)
	if a_fmt:
		s_f = numfmt.format_number(f, a_fmt, ',', '.')
	else:
		s_f = "%g" % f
	return s_f

def format_number_with_openpyxl(f, cell, wb):
	s_fmt = cell.number_format
	a_fmt = numfmt.extract_number_format(s_fmt)
	if a_fmt:
		return numfmt.format_number(f, a_fmt, ',', '.')
	else:
		return "%g" % f

format_number = format_number_with_openpyxl

def intToBase26(value):
	asciiA = ord('A')

	value += 1

	ret = ""
	while value != 0:
		mod = value % 26
		value = value // 26
		if mod == 0:
			mod = 26
			value -= 1

		ret = chr(asciiA + mod - 1) + ret

	return ret

def base26ToInt(value):
	asciiA = ord('A')

	ret = 0
	for s in value:
		ret = ret * 26 + ord(s) - asciiA + 1

	return ret - 1

to_str = tp0.to_str

FAST_CONVERTER = {
	"byte" : int,
	"short" : int,
	"int" : tp0.to_int,
	"float" : tp0.to_float,
	"string" : to_str,
	"bool" : tp0.to_bool,
	"boolean" : tp0.to_bool,
}

class ConverterInfo:
	def __init__(self, info):
		self.header = info[0]
		self.field = info[1]
		self.convert = info[2]
		self.is_default = info[3] if len(info) > 3 else False
		self.exist_default_value = len(info) > 4
		self.default_value = info[4] if len(info) > 4 else None

class Parser(object):

	def __init__(self, filename, module, sheet_index=0):
		super(Parser, self).__init__()

		self.key_name = getattr(module, "KEY_NAME", "ID")
		self.is_multi_key = getattr(module, "MULTI_KEY", False)

		self.filename = filename
		self.config = getattr(module, "CONFIG", None)

		self.header = None
		self.sheet_types = {}
		self.converters = None
		self.sheet = {}

		self.field_2_col = {}
		self.header_2_config = {}

		self.sheet_index = sheet_index
		self.header_row_index = 2
		self.type_row_index = 3
		self.data_row_index = 4

		self.header_data = None
		self.type_data = None

		self.set_module(module)

	def set_module(self, module):
		self.module = module
		self.is_quiet = getattr(module, "QUIET", False)

	def parse_header(self, header):
		pass

	def convert_cell(self, row, col, value, output_row, cell, book):
		converter = self.converters[col]
		if converter is None: return

		tp = type(value)

		if value is None:
			value = ""
		elif tp == float or tp == long or tp == int:
			value = format_number(value, cell, book)
		elif tp == unicode or tp == str:
			value = value.strip()
		else:
			msg = "不支持的数据类型: %s -> '%s'" % (type(value), value)
			raise ValueError, msg

		ret = None
		if value == "":
			if not converter.is_default:
				raise ValueError, "该项必填"

		else:
			col_type = to_str(self.type_data[col]).lower()
			try:
				method = FAST_CONVERTER[col_type]
			except Exception, e:
				print col, col_type
				print self.type_data
				raise Exception, e
			ret = method(value)

		if ret is None and converter.is_default:
			if not converter.exist_default_value:
				return
			ret = converter.default_value

		output_row[converter.field] = ret

	def parse_with_openpyxl(self):
		import openpyxl
		book = openpyxl.load_workbook(self.filename)

		sheets = book.worksheets
		if self.sheet_index >= len(sheets):
			raise ValueError, "The file has no sheet '%d'" % self.sheet_index

		table = sheets[self.sheet_index]
		rows = list(table.rows)

		# the row 0 is table header
		self.header_data = [cell.value for cell in rows[self.header_row_index]]
		self.parse_header(self.header_data)
		ncols = len(self.converters)

		self.type_data = [cell.value for cell in rows[self.type_row_index]]
		self.parse_type_row(self.type_data)

		if self.data_row_index >= len(rows):
			return

		# the remain rows is raw data.
		for r in xrange(self.data_row_index, len(rows)):
			cells = rows[r]
			# ignore the data below blank line
			first_value = cells[0].value
			if first_value == '' or first_value is None: break

			current_row_data = {}
			for c in xrange(ncols):
				cell = cells[c]
				value = cell.value
				try:
					self.convert_cell(r, c, value, current_row_data, cell, book)
				except Exception, e:
					traceback.print_exc()

					msg = "单元格(%d, %s) = [%s] 数据不合法" % (r + 1, intToBase26(c), to_str(value))
					if not xlsconfig.FORCE_RUN:
						raise ValueError, msg
					print msg

			self.add_row(current_row_data)

		return

	def do_parse(self):
		self.map_config_array_to_dict()
		self.parse_with_openpyxl()

	def add_row(self, current_row_data):
		if self.key_name not in current_row_data:
			raise ValueError, "The key '%s' was not found" % (self.key_name, )

		key_value = current_row_data.pop(self.key_name)
		
		if self.is_multi_key:
			row = self.sheet.setdefault(key_value, [])
			row.append(current_row_data)

		else:
			if key_value in self.sheet:
				raise ValueError, "duplicated key '%s' was found" % key_value

			self.sheet[key_value] = current_row_data

	def map_filed_to_col(self):
		field_2_col = {}
		for col, converter in self.converters.iteritems():
			if converter is None: continue

			field = converter.field
			field_2_col[field] = col

		self.field_2_col = field_2_col

	def map_config_array_to_dict(self):
		ret = {}
		for info in self.config:
			header = info[0]
			ret[header] = info
		self.header_2_config = ret

	def parse_type_row(self, type_row):
		removed_fields = getattr(self.module, "REMOVED_FIELDS", ())
		types = []

		all_fields = set()

		for info in self.config:
			text = info[0]
			field = info[1]
			if field in removed_fields: continue
			if field in all_fields:
				raise ValueError, "列名'%s'重复" % field
			all_fields.add(field)

			col = self.field_2_col.get(field)
			type = type_row[col] if col is not None else None
			types.append((col, field, text, type))

		self.sheet_types["main_sheet"] = types


class ParserByFieldName(Parser):

	def parse_header(self, header_row):
		self.converters = {}
		name_set = set()
		for col, col_name in enumerate(header_row):
			if col_name is None or col_name == "": break

			col_name = to_str(col_name)
			index = 2
			unique_name = col_name
			while unique_name in name_set:
				unique_name = col_name + str(index)
				index = index + 1
			col_name = unique_name
			name_set.add(col_name)

			converter = None
			cfg = self.header_2_config.get(col_name)
			if cfg is not None:
				converter = ConverterInfo(cfg)

			self.converters[col] = converter

			if converter is None and not self.is_quiet:
				print "警告：第(%s)列的表头'%s'没有被解析。%s" % (intToBase26(col), col_name, self.filename, )

		self.map_filed_to_col()
		return


class ParserByIndex(Parser):

	def set_module(self, module):
		super(ParserByIndex, self).set_module(module)
		self.config = module.CONFIG_INDEX

	def parse_header(self, header_row):
		self.converters = {}

		for col, col_name in enumerate(header_row):
			if col_name is None or col_name == "": break

			col_name = to_str(col_name)

			key = intToBase26(col)

			converter = None
			cfg = self.header_2_config.get(col_name)
			if cfg is not None:
				converter = ConverterInfo(cfg)
				converter.header = col_name

			self.converters[col] = converter

			if converter is None and not self.is_quiet:
				print "警告：第(%s)列的表头'%s'没有被解析。%s" % (intToBase26(col), col_name, self.filename, )

		self.map_filed_to_col()
		return

def createParser(input_file, module, sheet_index = 0):
	cls = None

	if getattr(module, "CONFIG_INDEX", None):
		cls = ParserByIndex
	else:
		cls = ParserByFieldName

	return cls(input_file, module, sheet_index)
