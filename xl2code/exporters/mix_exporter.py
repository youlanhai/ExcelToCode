# -*- coding: utf-8 -*-
import re
import os
import sys
import traceback
import xlsconfig
import util
import stages
from direct_exporter import DirectExporter
from tps import tp0
from parsers.base_parser import ConverterInfo

STAGES_INFO = [
	{"class" : "MergeSheets", },
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_BEGIN},
	{"class" : "ConvertField"},
	{"class" : "MergeField"},
	{"class" : "PostProcess"},
	{"class" : "PostCheck"},
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_FINAL},
	{"class" : "WriteConfigure"},
	{"class" : "WriteFileList"},
	{"class" : "RunCustomStage"},
]

class MixExporter(DirectExporter):

	STAGES_INFO = STAGES_INFO

	def __init__(self, input_path, exts):
		super(MixExporter, self).__init__(input_path, exts)
		self.converter_modules = {}

	def find_converter_info(self, infile):
		# 1. 搜索转换表
		for value in xlsconfig.CONVENTION_TABLE:
			pattern = value[0]
			compiled_pattern = re.compile(pattern)

			if compiled_pattern.match(infile):
				converter_name 	= value[1]
				new_name 	= value[2] if len(value) > 2 else None
				sheet_index = value[3] if len(value) > 3 else 0

				outfile = None
				if new_name is None:
					outfile = os.path.splitext(infile)[0]
				else:
					outfile = compiled_pattern.sub(new_name, infile)

				return (converter_name, outfile, sheet_index)

		# 2. 根据相同的目录结构去搜索
		outfile = os.path.splitext(infile)[0]
		converter_file = os.path.join(xlsconfig.CONVERTER_PATH, xlsconfig.CONVERTER_ALIAS, outfile + ".py")
		if os.path.exists(converter_file):
			converter_name = outfile.replace('/', '.').replace('\\', '.')
			return (converter_name, outfile, 0)

		# 3. 使用文件的名称当作转换器
		converter_name = os.path.basename(outfile)
		return (converter_name, outfile, 0)

	def find_converter(self, name):
		converter = self.converter_modules.get(name)
		if converter is None:
			converter = self.load_converter(name)
			self.converter_modules[name] = converter
		return converter

	def load_converter(self, name):
		converter = None
		full_path = os.path.join(xlsconfig.CONVERTER_PATH, xlsconfig.CONVERTER_ALIAS, name.replace('.', '//') + ".py")
		if not os.path.isfile(full_path):
			return None

		full_name = xlsconfig.CONVERTER_ALIAS + "." + name
		converter = util.import_converter(full_name)

		# 此名称有可能是文件夹，要加上校验
		if not hasattr(converter, "CONFIG"):
			return None

		converter._name = name
		return converter

