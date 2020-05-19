# -*- coding: utf-8 -*-
import re
import os
from copy import copy

import util
import writers
import xlsconfig
from exporters.data_module import DataModule
from BaseStage import BaseStage

class MergeSheets(BaseStage):

	def get_desc(self): return "合并分表"

	def process(self, exporter):
		self.merge(exporter, exporter.merge_patterns)

	def merge(self, exporter, merge_patterns):
		data_modules = exporter.data_modules

		for value in merge_patterns:
			outfile = value[0]

			sub_files = []

			for i in xrange(1, len(value)):
				compiled_pattern = re.compile(value[i])

				for infile in data_modules.iterkeys():
					if compiled_pattern.match(infile):
						sub_files.append(infile)

			if len(sub_files) > 0:
				data_module = self.merge_sub_files(exporter, outfile, sub_files)

				for sub_file in sub_files:
					data_modules.pop(sub_file)

				if data_module is not None:
					data_modules[outfile] = data_module

		return

	def merge_sub_files(self, exporter, outfile, sub_files):
		assert(len(sub_files) > 0)
		util.log("合并分表", outfile, "<-", sub_files)

		if outfile in exporter.data_modules:
			util.log_error("合并分表失败，目标表格'%s'已经存在", outfile)
			return None

		util.ensure_package_exist(xlsconfig.TEMP_PATH, outfile)
		new_path = os.path.join(xlsconfig.TEMP_PATH, outfile + ".py")

		info = None
		infiles = []
		sheet = {}

		for sub_file in sub_files:
			module = exporter.data_modules[sub_file]

			if info is None:
				info = copy(module.info)

			sheet.update(module.main_sheet)

			infiles.append(module.info["infile"])

		info["infile"] = ", ".join(infiles)
		info["outfile"] = outfile

		wt = writers.PyWriter(new_path, None)
		wt.max_indent = xlsconfig.TEMP_FILE_INDENT
		wt.begin_write()
		wt.write_value("path", outfile)
		wt.write_value("info", info)
		wt.write_value("main_sheet", sheet)
		wt.end_write()
		wt.close()

		converter = exporter.find_converter(info["parser"])
		return DataModule(outfile, info, sheet, converter)
