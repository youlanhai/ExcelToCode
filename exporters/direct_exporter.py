# -*- coding: utf-8 -*-
import os
import sys
import traceback

import xlsconfig
import util

from parsers import DirectParser
from base_exporter import BaseExporter

class DirectExporter(BaseExporter):
	def __init__(self, input_path, exts):
		super(DirectExporter, self).__init__(input_path, exts)
		self.parser_class = DirectParser

	def run(self):
		self.gather_excels()

		sys.path.insert(0, xlsconfig.CONVERTER_PATH)
		sys.path.insert(0, xlsconfig.TEMP_PATH)

		self.export_excels()

		# 合并分表
		self.merge_sheets()

		# 写出裸数据
		self.write_sheets(xlsconfig.EXPORT_STAGE_BEGIN)

		# 写出最终数据
		self.write_sheets(xlsconfig.EXPORT_STAGE_FINAL)

		self.write_file_list()
		
		self.write_configs()

		self.run_postprocessor()

		sys.path.remove(xlsconfig.CONVERTER_PATH)
		sys.path.remove(xlsconfig.TEMP_PATH)

	def export_excels(self):
		for infile in self.excel_files:
			converter_name, outfile, sheet_index = self.find_converter_info(infile)

			if self.export_excel_to_python(infile, outfile, converter_name, sheet_index):
				pass

			elif not xlsconfig.FORCE_RUN:
				return
		return

	def export_excel_to_python(self, infile, outfile, converter_name, sheet_index = 0):
		input_path = os.path.join(xlsconfig.INPUT_PATH, infile)
		output_path = os.path.join(xlsconfig.TEMP_PATH, outfile + ".py")

		if xlsconfig.FAST_MODE and util.if_file_newer(output_path, input_path):
			data_module = util.import_file(outfile)

		else:
			print infile, "-", converter_name
			parser = self.parser_class(input_path, None, sheet_index)
			try:
				parser.run()
			except:
				traceback.print_exc()
				return False

			# 这里有一次修改转换器的机会
			converter_name = parser.arguments.get("template", converter_name)

			data_module = self.create_data_module(infile, outfile, converter_name, parser)
			if data_module is None: return False

		merge_to_sheet = data_module.info["arguments"].get("mergeToSheet")
		if merge_to_sheet:
			self.add_merge_pattern(merge_to_sheet, outfile)

		self.store_data_module(data_module)
		return True

	def find_converter_info(self, infile):
		outfile = os.path.splitext(infile)[0]
		converter_name = os.path.basename(outfile)
		return (converter_name, outfile, 0)

	def add_merge_pattern(self, to_name, sub_name):

		# 如果目标表格存在，则追加到尾部
		for i, pattern in enumerate(self.merge_patterns):
			if to_name != pattern[0]: continue
			if sub_name in pattern: continue

			if not isinstance(pattern, list):
				pattern = list(pattern)
				self.merge_patterns[i] = pattern

			pattern.append(sub_name)
			return

		self.merge_patterns.append([to_name, sub_name])
		return





