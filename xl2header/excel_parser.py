# -*- coding: utf-8 -*-
from os import path
import json

import xlsconfig
import util
from util import log, log_error, ExcelToCodeException
import header_util
from header import Header

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

		self.header_root = Header.new_root()

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

		root = self.header_root

		for col, cell in enumerate(header_cells):
			title = self.parse_cell_value(cell)
			if not title:
				break

			if root.find_child(title):
				log_error("%s, 表头'%s'重复，at %s", self.filename, title, self.row_col_str(self.header_row_index, col))
				continue

			header = Header()
			header.index = col
			header.title = title
			header.field = self.parse_cell_value(field_cells[col])
			header.field_type = self.parse_cell_value(type_cells[col])
			root.add_child(header)

		if len(root.children) == 0:
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
			self.field_row_index -= self.vertical_start_row
			self.type_row_index -= self.vertical_start_row
			self.data_row_index -= self.vertical_start_row

		return

	def get_colum_cells(self, col):
		ret = []
		worksheet = self.worksheet
		for row in xrange(self.vertical_start_row, self.max_row):
			ret.append(worksheet[row + 1][col])
		return ret

	def extract_cells(self, index):
		if self.is_vertical:
			return self.get_colum_cells(index)
		else:
			return self.worksheet[index + 1]

	def row_col_str(self, row, col):
		return "%d:%s" % (row, util.int_to_base26(col))

	def save(self, output_path):
		output_path = output_path.decode('utf-8')
		util.ensure_folder_exist(output_path)
		header_util.save_header_list(output_path, self.header_root, self.arguments)

	def save_test(self, output_path):
		tree = header_util.gen_header_tree(self.header_root)
		list = header_util.gen_header_list(tree)

		tree_data = []
		self.save_as_tree(tree, tree_data)

		list_data = []
		self.save_as_list(list, list_data)

		arguments = self.arguments

		data = {
			"arguments" : arguments,
			# "header" : self.headers,
			"tree" : tree_data,
			"list" : list_data,
		}

		output_path = output_path.decode('utf-8')
		util.ensure_folder_exist(output_path)
		with open(output_path, "wb") as f:
			json.dump(data, f, indent = 4, sort_keys=True, ensure_ascii = False)

	def save_as_tree(self, node, data):
		self.save_tree_children(node.children, data)

	def save_tree_children(self, children, data):
		for child in children:
			v = {
				"title" 	: child.title,
				"field" 	: child.field,
				"field_type" : child.field_type,
				"type" 		: child.type,
				"index" 	: child.index,
				"end_title" : child.end_title,
				"end_index" : child.end_index,
			}

			if child.children is not None:
				children_data = []
				self.save_tree_children(child.children, children_data)
				v["children"] = children_data

			data.append(v)

	def save_as_list(self, node, data):
		for child in node.children:
			data.append("%s, %s, %s" % (child.title, child.field, child.field_type))
