# -*- coding: utf-8 -*-
import os
import re
import traceback

import xlsconfig
import util

from parsers import ConfigParser
from base_exporter import BaseExporter

STAGES_INFO = [
	{"class" : "ParseExcel"},
	{"class" : "MergeSheets", },
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_RAW},
	{"class" : "MergeField"},
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_BEGIN},
	{"class" : "PostProcess"},
	{"class" : "PostCheck"},
	{"class" : "ExtractConstant"},
	{"class" : "MergeFiles"},
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_FINAL},
	{"class" : "WriteConfigure"},
	{"class" : "WriteFileList"},
	{"class" : "RunCustomStage"},
]

class ConfigExporter(BaseExporter):
	STAGES_INFO = STAGES_INFO

	def __init__(self, input_path, exts):
		super(ConfigExporter, self).__init__(input_path, exts)
		self.converter_modules = {}
		self.parser_class = ConfigParser

	def find_converter(self, name):
		converter = self.converter_modules.get(name)
		if converter is None:
			full_name = xlsconfig.CONVERTER_ALIAS + "." + name
			converter = util.import_converter(full_name)
			converter._name = name
			self.converter_modules[name] = converter
		return converter

	def export_excels(self):
		file_2_converter = {}

		for value in xlsconfig.CONVENTION_TABLE:
			pattern = value[0]
			converter_name = value[1]
			new_name = value[2] if len(value) > 2 else None
			sheet_index = value[3] if len(value) > 3 else 0

			compiled_pattern = re.compile(pattern)

			for infile in self.excel_files:
				if not compiled_pattern.match(infile):
					continue
				if infile in file_2_converter:
					util.log_error("文件'%s'匹配到了多个转换器", infile)

				outfile = None
				if new_name is None:
					outfile = os.path.splitext(infile)[0]
				else:
					outfile = compiled_pattern.sub(new_name, infile)

				if xlsconfig.OUTPUT_PATH_TO_LOWER:
					outfile = outfile.lower()

				if self.export_excel_to_python(infile, outfile, converter_name, sheet_index):
					pass

				elif not xlsconfig.FORCE_RUN:
					return

				file_2_converter[outfile] = value[1]
		return

	def export_excel_to_python(self, infile, outfile, converter_name, sheet_index = 0):
		converter = self.find_converter(converter_name)

		input_path = os.path.join(self.input_path, infile)

		util.log(infile, "-", converter_name)
		parser = self.parser_class(input_path, converter, sheet_index)
		try:
			parser.run()
		except:
			traceback.print_exc()
			return False

		data_module = self.create_data_module(infile, outfile, converter_name, parser)
		if data_module is None:
			return False

		self.store_data_module(data_module)
		return True
