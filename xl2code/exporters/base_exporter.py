# -*- coding: utf-8 -*-
import os
import sys

import xlsconfig
import writers
import stages
import util
from tps import tp0
from data_module import DataModule, NewConverter


class BaseExporter(object):
	def __init__(self, input_path, exts):
		super(BaseExporter, self).__init__()
		self.input_path = input_path
		self.exts = exts or (".xlsx", )

		self.excel_files = None
		self.data_modules = {}

		self.configures = {}
		self.merge_patterns = list(xlsconfig.MERGE_TABLE)

		self.parser_class = None

		self.stages_info = getattr(xlsconfig, "EXPORTER_STAGES", self.STAGES_INFO)

	def run(self):
		self.gather_excels()

		sys.path.insert(0, xlsconfig.CONVERTER_PATH)
		sys.path.insert(0, xlsconfig.TEMP_PATH)

		# export excels to temp python
		self.export_excels()

		for stage_info in self.stages_info:
			stage_class = stages.classes.get(stage_info["class"], None)
			if stage_class is None:
				util.log_error("Failed find stage '%s'", stage_info["class"])
				break
			
			stage = stage_class(stage_info)
			print "=== %s ===" % stage.get_desc()
			stage.process(self)

		sys.path.remove(xlsconfig.CONVERTER_PATH)
		sys.path.remove(xlsconfig.TEMP_PATH)

	def export_excels(self):
		pass

	def find_converter(self, converter_name):
		pass

	def gather_excels(self):
		print "=== 搜索Excel文件 ..."

		self.excel_files = util.gather_all_files(self.input_path, self.exts)
		print "发现 %d 个excel文件" % len(self.excel_files)

	def store_data_module(self, data_module):
		module_info = data_module.info
		infile = module_info["infile"]
		outfile = module_info["outfile"]
		converter_name = module_info["parser"]

		converter = self.configures.get(converter_name)
		if converter is None:
			converter = NewConverter(converter_name, module_info["sheet_types"]["main_sheet"], module_info["arguments"], infile)
			self.configures[converter_name] = converter
		else:
			if not converter.compare_types(module_info["sheet_types"]["main_sheet"], infile):
				return False

		# 真实的转换器
		data_module.converter = self.find_converter(converter_name)
		self.data_modules[outfile] = data_module
		return True

	def create_data_module(self, infile, outfile, converter_name, parser):
		info = {
			"infile" : infile,
			"outfile" : outfile,
			"parser" : converter_name,
			"multi_key" : parser.is_multi_key,
			"key_name" : parser.key_name,
			"arguments" : parser.arguments,
			"sheet_types" : {"main_sheet" : parser.sheet_types},
		}

		util.ensure_package_exist(xlsconfig.TEMP_PATH, outfile)
		output_path = os.path.join(xlsconfig.TEMP_PATH, outfile + ".py")

		wt = writers.PyWriter(output_path, None)
		wt.max_indent = xlsconfig.TEMP_FILE_INDENT
		wt.begin_write()

		wt.write_value("path", outfile)
		wt.write_sheet("info", info)
		wt.write_sheet("main_sheet", parser.sheet)

		wt.end_write()
		wt.close()

		return DataModule(outfile, info, parser.sheet)
