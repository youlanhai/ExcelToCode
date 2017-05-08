# -*- coding: utf-8 -*-

from copy import copy
from json_writer import JsonWriter
import util

# 当前Writer的功能是生成java专用的json格式，而不是java代码
# json格式：
#   整体是一个字典，包含两个元素，header和body
#   header有两行：
#       第一行是表头
#       第二行是列名
#	body是一个二维数组：
#       对应了excel的各个单元


class JavaWriter(JsonWriter):

	def begin_write(self):
		super(JavaWriter, self).begin_write()

		module_info = self.data_module.info
		parser_name = module_info["parser"].split('.')[-1]
		class_name = util.to_class_name(parser_name)
		self.write_value("class", class_name)

		sheet_types = module_info["sheet_types"]["main_sheet"]

		self.fields = [v[1] for v in sheet_types]
		col_names = [v[2] for v in sheet_types]
		types = [v[3] for v in sheet_types]

		headers = [col_names, self.fields, ]
		self.write_value("header", headers, 2)

	def write_sheet(self, name, sheet):
		if name != "main_sheet": return

		key_field = self.fields[0]
		body = []
		for k, rows in sheet.iteritems():
			# 需要考虑到重复key的情况，每个rows会是一个数组。
			# 简单起见，单行的情况，也认为是多行的一个特例。

			if not isinstance(rows, list):
				rows = [rows, ]

			for row in rows:
				new_row = copy(row)

				new_row[key_field] = k

				body.append(new_row)

		body.sort(key = lambda v: v[key_field])

		self.write_value("body", body, 2)

	def write_module(self, module): pass
