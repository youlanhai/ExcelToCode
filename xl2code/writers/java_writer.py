# -*- coding: utf-8 -*-
from .json_writer import JsonWriter
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

		self.is_multi_key = module_info["multi_key"]
		self.write_value("multiKey", self.is_multi_key)

		sheet_types = module_info["sheet_types"]["main_sheet"]

		texts = list(sheet_types.keys())
		texts.sort()

		fields = [sheet_types[field][1] for field in texts]
		headers = [texts, fields, ]
		self.write_value("header", headers, 2)

	def write_sheet(self, name, sheet):
		if name != "main_sheet":
			return

		max_indent = self.max_indent
		if self.is_multi_key:
			max_indent += 1

		body = []

		keys = list(sheet.keys())
		keys.sort()
		for k in keys:
			row = sheet[k]
			new_row = None

			if isinstance(row, list):
				new_row = []

				for sub_row in row:
					new_row.append(sub_row)
			else:
				new_row = row

			body.append(new_row)

		self.write_value("body", body, max_indent)

	def write_module(self, module):
		pass
