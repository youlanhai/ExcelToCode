# -*- coding: utf-8 -*-

import traceback
import xlsconfig
import util
from util import ExcelToCodeException, log_error
from tps import tp0, convention
import csv

class ConverterInfo:
	def __init__(self, info, column = None):
		self.header = info[0]
		self.field = info[1]
		self.convert = info[2]
		self.can_default = info[3] if len(info) > 3 else False
		self.exist_default_value = len(info) > 4
		self.default_value = info[4] if len(info) > 4 else None
		self.column = column

class BaseParser(object):

	def __init__(self, filename, module, sheet_index=0):
		super(BaseParser, self).__init__()

		# 表格key名。调试用
		self.key_name = "ID"
		self.is_multi_key = False

		self.filename = filename
		self.module = module
		# sheet页索引
		self.sheet_index = sheet_index

		# 转换器。列索引 -> 转换器(ConverterInfo)
		self.converters = {}

		# 最终生成的数据表。key是第一格对应的数据。
		# 如果表格是multi_key，则value是一个数组，包含了所有key相同的行。
		self.sheet = {}

		# 表头的类型数据。
		self.sheet_types = {}

		# 表头映射到列索引
		self.header_2_col = {}
		# 表头数组。也就是连续的表头列数，空列右侧的内容会被忽略。
		self.headers = []

		# 每一列的默认值。列索引 -> 默认值
		self.default_values = {}

		self.argument_row_index = xlsconfig.SHEET_ROW_INDEX["argument"]
		self.header_row_index 	= xlsconfig.SHEET_ROW_INDEX["header"]
		self.data_row_index 	= xlsconfig.SHEET_ROW_INDEX["data"]
		self.default_value_row_index = xlsconfig.SHEET_ROW_INDEX.get("default", -1)

		# 表格是否是垂直排列
		self.is_vertical = False
		# 如果是垂直排列的话，从第几行开始才是真正的数据
		self.vertical_start_row = xlsconfig.SHEET_ROW_INDEX.get("verticalStartRow", 2)

		self.workbook = None
		self.worksheet = None

		self.version = None

		# excel表头第一行的参数
		self.arguments = {}

		# 上一次解析行的key
		self.last_key = None

	def run(self):
		self.do_parse()

	def get_default_value(self, col):
		value = self.default_values.get(col, "")
		if value == '!':
			raise ExcelToCodeException, "该项必填"
		value = value.replace("\\!", "!")
		return value

	def convert_cell(self, row, col, value):
		converter = self.converters[col]
		if converter is None:
			return None

		if value == "":
			value = self.get_default_value(col)

		ret = None
		if value == "":
			if not converter.can_default:
				raise ExcelToCodeException, "该项必填"

		else:
			try:
				ret = converter.convert(value)
			except Exception, e:
				msg = "类型转换失败fun = %s, value = %s, 异常：%s" % (str(converter.convert), str(value), str(e))
				raise ExcelToCodeException, msg

		if ret is None and converter.exist_default_value:
			ret = converter.default_value

		return ret

	def do_parse(self):
		csvReader = None
		with open(self.filename.decode("utf-8"), "rb") as f:
			csvReader = csv.reader(f)

			self.worksheet = []
			for row in csvReader:
				self.worksheet.append(row)
		
		self.max_row = len(self.worksheet)
		if self.max_row == 0:
			print "表格为空：", self.filename
			return

		self.max_column = len(self.worksheet[0])

		self.parse_arguments(self.extract_cells(self.argument_row_index))

		if self.version is None:
			log_error("无效的数据表文件，必须存在版本号信息")
			return

		self.parse_header(self.extract_cells(self.header_row_index))

		if self.default_value_row_index >= 0:
			self.parse_defaults(self.extract_cells(self.default_value_row_index))

		if self.is_vertical:
			self.parse_by_vertical(self.worksheet)
		else:
			self.parse_by_horizontal(self.worksheet)
		return

	def is_blank_line(self, cells, count):
		for i in xrange(count):
			v = cells[i]
			if v != '' and v is not None:
				return False

		return True

	def parse_cells(self, r, cells):
		max_cols = len(self.headers)

		# 遇到空白行，表示解析完成
		if self.is_blank_line(cells, max_cols):
			return

		# 如果key是空，自动复制上一行key
		first_value = cells[0]
		if first_value == '' or first_value is None:
			cells[0] = self.last_key
		else:
			self.last_key = first_value

		current_row_data = []
		for c in xrange(max_cols):
			cell_value = cells[c]
			result_value = None
			try:
				result_value = self.convert_cell(r, c, cell_value)
			except ExcelToCodeException, e:
				# traceback.print_exc()
				log_error("单元格 %s = [%s] 数据解析失败。原因：%s", self.row_col_str(r, c), str(cell_value), str(e))

			current_row_data.append(result_value)

		self.add_row(current_row_data)
		return True

	def parse_by_horizontal(self, worksheet):
		for r in xrange(self.data_row_index, self.max_row):
			cells = worksheet[r]
			if not self.parse_cells(r, cells):
				break
		return

	def parse_by_vertical(self, worksheet):
		for c in xrange(self.data_row_index, self.max_column):
			cells = self.get_colum_cells(c)
			if not self.parse_cells(c, cells):
				break
		return

	def add_row(self, current_row_data):
		key_value = current_row_data[0]
		
		if self.is_multi_key:
			row = self.sheet.setdefault(key_value, [])
			row.append(current_row_data)

		else:
			if key_value in self.sheet:
				raise ExcelToCodeException, "Key'%s'重复" % key_value

			self.sheet[key_value] = current_row_data

	def parse_header(self, cells):
		self.headers = cells

		for col, header in enumerate(cells):
			if header == "":
				self.headers = cells[:col]
				break

			if header in self.header_2_col:
				log_error("表头'%s'重复，at %s", header, self.row_col_str(self.header_row_index, col))
				continue

			self.header_2_col[header] = col

		if len(self.headers) == 0:
			return log_error("Except表'%s'表头数量不能为0", self.filename)

		return

	def parse_arguments(self, cells):
		compatible_posfix = '：'

		self.arguments = {}
		for col in xrange(0, len(cells), 2):
			header = cells[col]
			if header is None: break

			if header.endswith(compatible_posfix):
				split = len(header) - len(compatible_posfix)
				header = header[:split]

			converter = xlsconfig.ARGUMENT_CONVERTER.get(header)
			if converter is None: continue

			field, type = converter
			method = convention.type2function(type)

			value = cells[col + 1]
			ret = None
			try:
				ret = method(value)
			except:
				traceback.print_exc()

				log_error("参数转换失败，%s = [%s]", self.row_col_str(self.argument_row_index, col), value)

			self.arguments[field] = ret

		self.version = self.arguments.get("version")

		self.is_vertical = self.arguments.get("vertical", False)
		if self.is_vertical:
			self.header_row_index -= self.vertical_start_row
			self.data_row_index -= self.vertical_start_row
			self.default_value_row_index -= self.vertical_start_row

		if self.default_value_row_index < 0:
			if self.arguments.get("existDefaultRow", False):
				self.default_value_row_index = self.data_row_index
				self.data_row_index += 1

		multi_key = self.arguments.get("multiKey")
		if multi_key is not None:
			self.is_multi_key = multi_key
		return

	def parse_defaults(self, cells):
		default_values = {}
		for col, value in enumerate(cells):
			if value != "":
				default_values[col] = value

		self.default_values = default_values

	def get_colum_cells(self, col):
		ret = []
		worksheet = self.worksheet
		for row in xrange(self.vertical_start_row, self.max_row):
			ret.append(worksheet[row][col])
		return ret

	def extract_cells(self, index):
		if self.is_vertical:
			return self.get_colum_cells(index)
		else:
			return self.worksheet[index]

	def row_col_str(self, row, col):
		real_r, real_c = row, col
		if self.is_vertical:
			real_r = col + self.vertical_start_row
			real_c = row
		return "%d:%s" % (real_r, util.int_to_base26(real_c))
