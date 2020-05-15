# -*- coding: utf-8 -*-
from os import path
import json

import xlsconfig
import util
from util import log, log_error, ExcelToCodeException
from merge_field import MergeField

FORMAT_MAP = {
	type(None) : lambda value, cell, parser: "",
	int 	: util.format_number,
	long 	: util.format_number,
	float 	: util.format_number,
	bool 	: lambda value, cell, parser: str(value),
	str 	: lambda value, cell, parser: value.strip(),
	unicode : lambda value, cell, parser: value.encode("utf-8").strip()
}

class ExcelParser(object):

	FORMAT_MAP = FORMAT_MAP

	def __init__(
		self,
		filename,
		sheet_index = 0,
		export_all_sheet = False,
		max_row = 65535,
		max_column = 1000,
	):
		super(ExcelParser, self).__init__()

		# 表格路径
		self.filename = filename

		self.sheet_index = 0
		self.export_all_sheet = export_all_sheet

		self.max_row = max_row
		self.max_column = max_column

		# 当前的Excel表
		self.workbook = None
		# 当前的sheet页
		self.worksheet = None

		self.headers = {}
		self.header_list = []

		self.argument_row_index = xlsconfig.SHEET_ROW_INDEX["argument"]
		self.header_row_index = xlsconfig.SHEET_ROW_INDEX["header"]
		self.field_row_index = xlsconfig.SHEET_ROW_INDEX["field"]
		self.type_row_index = xlsconfig.SHEET_ROW_INDEX["type"]
		self.data_row_index = xlsconfig.SHEET_ROW_INDEX["data"]

		# 表格是否是垂直排列
		self.is_vertical = False
		# 如果是垂直排列的话，从第几行开始才是真正的数据
		self.vertical_start_row = xlsconfig.SHEET_ROW_INDEX.get("verticalStartRow", 2)

	# 将单元格数据转换成字符串形式。
	def parse_cell_value(self, cell):
		value = cell.value
		tp = type(value)

		method = self.FORMAT_MAP.get(tp)
		if method:
			return method(value, cell, self)

		raise ExcelToCodeException("不支持的数据类型: %s" % str(tp), self.filename)

	def parse(self):
		try:
			import openpyxl
		except:
			return log_error("请安装插件: openpyxl")

		self.workbook = openpyxl.load_workbook(self.filename.decode("utf-8"))
		self.worksheet = self.workbook.worksheets[self.sheet_index]
		self.max_row = min(self.max_row, self.worksheet.max_row)
		self.max_column = min(self.max_column, self.worksheet.max_column)

		# 注意：worksheet的行列索引是从"1"开始的

		self.parse_arguments()
		self.parse_header()
		return

	def parse_header(self):
		header_cells = self.extract_cells(self.header_row_index)
		field_cells = self.extract_cells(self.field_row_index)
		type_cells = self.extract_cells(self.type_row_index)

		for col, cell in enumerate(header_cells):
			title = self.parse_cell_value(cell)
			if not title:
				break

			if title in self.headers:
				log_error("%s, 表头'%s'重复，at %s", self.filename, title, self.row_col_str(self.header_row_index, col))
				continue

			header = {
				"title" : title,
				"index" : col,
				"field" : self.parse_cell_value(field_cells[col]),
				"type" : self.parse_cell_value(type_cells[col]),
			}
			self.headers[title] = header
			self.header_list.append(header)

		if len(self.headers) == 0:
			return log_error("%s, 表头数量不能为0", self.filename)

		return

	def parse_arguments(self):
		cells = self.extract_cells(self.argument_row_index)
		compatible_posfix = '：'

		self.arguments = {}
		for col in xrange(0, len(cells), 2):
			header = self.parse_cell_value(cells[col])
			if header is None:
				break

			if header.endswith(compatible_posfix):
				split = len(header) - len(compatible_posfix)
				header = header[:split]

			converter = xlsconfig.ARGUMENT_CONVERTER.get(header)
			if converter is None:
				continue

			field, type = converter
			value = self.parse_cell_value(cells[col + 1])
			self.arguments[field] = value

		self.is_vertical = self.arguments.get("vertical", False)
		if self.is_vertical:
			self.header_row_index -= self.vertical_start_row
			self.type_row_index -= self.vertical_start_row
			self.data_row_index -= self.vertical_start_row

		return

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
			return self.worksheet[index + 1]

	def row_col_str(self, row, col):
		return "%d:%s" % (row, util.int_to_base26(col))

	def save(self, output_path):
		merge = MergeField(self.header_list)
		merge.merge_fields()

		data = {
			"arguments" : self.arguments,
			# "header" : self.headers,
			"fields" : merge.fields,
		}
		output_path = output_path.decode('utf-8')
		util.ensure_folder_exist(output_path)
		with open(output_path, "wb") as f:
			json.dump(data, f, indent = 4, sort_keys=True, ensure_ascii = False)

			f.write("\n")
			text = merge.to_list()
			f.write(text)
