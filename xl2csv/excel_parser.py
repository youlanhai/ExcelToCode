# -*- coding: utf-8 -*-
from os import path
import csv
import datetime

from . import util
from .util import log, log_error, ExcelToCodeException

FORMAT_MAP = {
	type(None) : lambda value, cell, parser: "",
	int 	: util.format_number,
	float 	: util.format_number,
	bool 	: lambda value, cell, parser: str(value),
	str 	: lambda value, cell, parser: value.strip(),
	datetime.time : lambda value, cell, parser: str(value),
	datetime.datetime : lambda value, cell, parser: str(value),
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

		self.sheet = []
		self.sheets = []
		self.sheet_names = []

		self.sheet_index = 0
		self.export_all_sheet = export_all_sheet

		self.max_row = max_row
		self.max_column = max_column

		# 当前的Excel表
		self.workbook = None
		# 当前的sheet页
		self.worksheet = None

	# 将单元格数据转换成字符串形式。
	def extract_cell_value(self, cell):
		value = cell.value
		tp = type(value)
		method = self.FORMAT_MAP.get(tp)
		if method:
			return method(value, cell, self)

		raise ExcelToCodeException("不支持的数据类型: %s" % str(tp))

	def parse(self):
		try:
			import openpyxl
		except:
			return log_error("请安装插件: openpyxl")

		# 支持excel公式
		self.workbook = openpyxl.load_workbook(self.filename, data_only = True)

		worksheets = self.workbook.worksheets
		self.sheets = [None] * len(worksheets)
		self.sheet_names = [None] * len(worksheets)

		if self.export_all_sheet:
			for i, worksheet in enumerate(worksheets):
				self.parse_sheet(i, worksheet)
		else:
			if self.sheet_index >= len(worksheets):
				log_error("%s, 没有子表'%d'", self.filename, self.sheet_index)
			else:
				self.parse_sheet(self.sheet_index, worksheets[self.sheet_index])
		return

	def parse_sheet(self, i, worksheet):
		self.worksheet = worksheet

		# 注意：worksheet的行列索引是从"1"开始的

		if worksheet.max_column > self.max_column:
			log("warn: Excel '%s' 列数过多：%d" % (self.filename, worksheet.max_column))
		if worksheet.max_row > self.max_row:
			log("warn: Excel '%s' 行数过多：%d" % (self.filename, worksheet.max_row))

		self.current_sheet_index = i
		self.sheet = []
		self.sheets[i] = self.sheet
		self.sheet_names[i] = worksheet.title

		row_count = min(worksheet.max_row, self.max_row)
		col_count = min(worksheet.max_column, self.max_column)

		for r in range(row_count):
			cells = worksheet[r + 1]

			# 遇到空白行，表示解析完成
			if r > 5 and self.is_blank_line(cells, col_count):
				break

			if not self.parse_cells(r, cells, col_count):
				break

		return

	def is_blank_line(self, cells, col_count):
		for i in range(col_count):
			v = cells[i].value
			if v != '' and v is not None:
				return False

		return True

	def parse_cells(self, r, cells, col_count):
		current_row_data = []
		for c in range(col_count):
			value = None
			try:
				value = self.extract_cell_value(cells[c])
			except ExcelToCodeException as e:
				value = str(cells[c].value)
				log_error("%s, 单元格 %s = [%s] 数据解析失败。原因：%s", self.filename, self.row_col_str(r, c), value, str(e))

			current_row_data.append(value)

		self.sheet.append(current_row_data)
		return True

	def row_col_str(self, row, col):
		return "%d:%s" % (row, util.int_to_base26(col))

	def save(self, output_path):
		if self.export_all_sheet:
			output_name = path.splitext(output_path)[0]
			for i, sheet in enumerate(self.sheets):
				sheet_name = self.sheet_names[i]
				sheet_path = "%s_%s.csv" % (output_name, sheet_name)
				self.save_sheet(sheet, sheet_path)
		else:
			self.save_sheet(self.sheet, output_path)

	def save_sheet(self, sheet, output_path):
		util.ensure_folder_exist(output_path)
		with open(output_path, "w", encoding = "utf-8") as f:
			writer = csv.writer(f)
			writer.writerows(sheet)
