# -*- coding: utf-8 -*-
import re
import os
from copy import copy

import util
import writers
from exporters.data_module import DataModule
from BaseStage import BaseStage

class MergeSheets(BaseStage):

	def get_desc(self): return "合并分表"

	def process(self, exporter):
		data_modules = exporter.data_modules

		for value in exporter.merge_patterns:
			outfile = value[0]

			sub_files = []

			for i in xrange(1, len(value)):
				compiled_pattern = re.compile(value[i])

				for infile in data_modules.iterkeys():
					if compiled_pattern.match(infile):
						sub_files.append(infile)

			if len(sub_files) > 0:
				data_module = self.merge_sub_files(outfile, sub_files)

				for sub_file in sub_files:
					data_modules.pop(sub_file)

				data_modules[outfile] = data_module

		return

	def merge_sub_files(self, exporter, outfile, sub_files):
		assert(len(sub_files) > 0)
		print "合并", outfile, "<-", sub_files

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

			#os.remove(os.path.join(TEMP_PATH, sub_file + ".py"))

		info["infile"] = ", ".join(infiles)
		info["outfile"] = outfile

		wt = writers.PyWriter(new_path, None)
		wt.max_indent = TEMP_FILE_INDENT
		wt.begin_write()
		wt.write_value("path", outfile)
		wt.write_sheet("info", info)
		wt.write_sheet("main_sheet", sheet)
		wt.end_write()
		wt.close()

		converter = exporter.find_converter(info["parser"])
		return DataModule(outfile, info, sheet, converter)
