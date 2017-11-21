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
	{"class" : "ParseExcel"},
	{"class" : "MergeSheets", },
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_RAW},
	{"class" : "ConvertField"},
	{"class" : "ExtractLocale"},
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

class MixExporter(DirectExporter):

	STAGES_INFO = STAGES_INFO

	def __init__(self, input_path, exts):
		super(MixExporter, self).__init__(input_path, exts)
		self.converter_modules = {}
		self.converter_path = os.path.join(xlsconfig.CONVERTER_PATH, xlsconfig.CONVERTER_ALIAS)

	def match_converter(self, name):
		path = os.path.join(self.converter_path, name + ".py")
		if os.path.exists(path):
			return name

		basename = os.path.basename(name)
		if name != basename:
			path = os.path.join(self.converter_path, basename + ".py")
			if os.path.exists(path):
				return basename

		return name

	def find_converter(self, name):
		converter = self.converter_modules.get(name)
		if converter is None:
			converter = self.load_converter(name)
			self.converter_modules[name] = converter
		return converter

	def load_converter(self, name):
		converter = None
		full_path = os.path.join(self.converter_path, name.replace('.', '/') + ".py")
		if not os.path.isfile(full_path):
			return None

		full_name = xlsconfig.CONVERTER_ALIAS + "." + name
		converter = util.import_converter(full_name)

		# 此名称有可能是文件夹，所有要进行校验
		if not hasattr(converter, "CONFIG"):
			return None

		converter._name = name
		return converter

