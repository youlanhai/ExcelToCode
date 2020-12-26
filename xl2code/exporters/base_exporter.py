# -*- coding: utf-8 -*-
import os
import sys
import traceback

import xlsconfig
import writers
from . import stages
import util
from tps import convention
from .data_module import DataModule, NewConverter


class BaseExporter(object):

	# 默认的导表步骤
	STAGES_INFO = {}

	def __init__(self, input_path, exts):
		super(BaseExporter, self).__init__()
		self.input_path = input_path
		self.exts = exts or (".xlsx", )

		self.excel_files = None
		self.data_modules = {}

		self.configures = {}
		self.merge_patterns = list(xlsconfig.MERGE_TABLE)
		self.merge_file_patterns = []

		self.parser_class = None

		self.stages_info = getattr(xlsconfig, "EXPORTER_STAGES", self.STAGES_INFO)

		self.data_temp_path = os.path.join(xlsconfig.TEMP_PATH, "data")
		util.safe_makedirs(self.data_temp_path)

		self.python_search_paths = [xlsconfig.CONVERTER_PATH, ]

	def run(self):
		convention.update_functions()

		for path in self.python_search_paths:
			sys.path.insert(0, path)

		for stage_info in self.stages_info:
			stage_class = stages.CLASSES.get(stage_info["class"], None)
			if stage_class is None:
				util.log_error("Failed find stage '%s'", stage_info["class"])
				break

			stage = stage_class(stage_info)
			try:
				util.log("=== %s ===" % stage.get_desc())
				stage.process(self)
			except util.ExcelToCodeException as e:
				raise e
			except Exception as e:
				traceback.print_exc()
				raise util.ExcelToCodeException(stage.get_desc())

		for path in self.python_search_paths:
			sys.path.remove(path)

	def export_excels(self):
		pass

	def find_converter(self, converter_name):
		pass

	def gather_excels(self):
		util.log("=== 搜索Excel文件 ...")

		self.excel_files = util.gather_all_files(self.input_path, self.exts)
		util.log("发现 %d 个excel文件" % len(self.excel_files))

	def store_data_module(self, data_module):
		module_info = data_module.info
		infile = module_info["infile"]
		outfile = module_info["outfile"]
		converter_name = module_info["parser"]

		converter = self.configures.get(converter_name)
		if converter is None:
			sheet_types = module_info["sheet_types"]["main_sheet"]
			converter = NewConverter(converter_name, sheet_types, module_info["arguments"], infile)
			self.configures[converter_name] = converter
		else:
			if not converter.compare_types(module_info["sheet_types"]["main_sheet"], infile):
				return False

		# 真实的转换器
		data_module.converter = self.find_converter(converter_name)
		self.data_modules[outfile] = data_module
		return True

	def create_data_module(self, infile, outfile, converter_name, parser, info = None):
		info = info or {}
		info["infile"] = infile
		info["outfile"] = outfile
		info["parser"] = converter_name
		info["multi_key"] = parser.is_multi_key
		info["key_name"] = parser.key_name
		info["arguments"] = parser.arguments
		info["sheet_types"] = {"main_sheet" : parser.sheet_types}

		data_module = DataModule(outfile, info, parser.sheet)

		if xlsconfig.SAVE_MIDDLE_DATA_FILE:
			self.save_data_module_to_file(data_module)

		return data_module

	def save_data_module_to_file(self, data_module):
		info = data_module.info
		outfile = info["outfile"]

		util.ensure_package_exist(self.data_temp_path, outfile)
		output_path = os.path.join(self.data_temp_path, outfile + ".py")

		wt = writers.PyWriter(output_path, None)
		wt.max_indent = xlsconfig.TEMP_FILE_INDENT
		wt.begin_write()

		wt.write_value("path", outfile)
		wt.write_value("info", info)
		wt.write_value("main_sheet", data_module.main_sheet)

		wt.end_write()
		wt.close()
