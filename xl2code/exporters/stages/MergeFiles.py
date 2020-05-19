# -*- coding: utf-8 -*-
import os

import util
import writers
import xlsconfig
from exporters.data_module import DataModule
from MergeSheets import MergeSheets

class MergeFiles(MergeSheets):

	def get_desc(self): return "合并文件"

	def process(self, exporter):
		self.merge(exporter, exporter.merge_file_patterns)

	def merge_sub_files(self, exporter, outfile, sub_files):
		assert(len(sub_files) > 0)
		util.log("合并文件", outfile, "<-", sub_files)

		if outfile in exporter.data_modules:
			util.log_error("合并文件失败，目标文件'%s'已经存在", outfile)
			return None

		util.ensure_package_exist(xlsconfig.TEMP_PATH, outfile)
		new_path = os.path.join(xlsconfig.TEMP_PATH, outfile + ".py")

		info = {
			"arguments" : {},
			"parser" : outfile.replace('/', '.'),
			"outfile" : outfile,
			"multi_key": False,
			"merged" : True,
		}
		infiles = []
		sheets = {}
		types = {}

		for sub_file in sub_files:
			module = exporter.data_modules[sub_file]

			name = os.path.basename(sub_file)
			if name in sheets:
				util.log_error("待合并的文件不能重名: %s", name)

			sheets[name] = module.main_sheet
			types[name] = module.info["sheet_types"]["main_sheet"]

			extra_sheets = getattr(module, "extra_sheets", None)
			if extra_sheets:
				sheets.update(extra_sheets)

			infiles.append(module.info["infile"])

		info["infile"] = ", ".join(infiles)
		info["outfile"] = outfile
		info["sheet_types"] = types

		wt = writers.PyWriter(new_path, None)
		wt.max_indent = xlsconfig.TEMP_FILE_INDENT
		wt.begin_write()
		wt.write_value("path", outfile)
		wt.write_sheet("info", info)
		wt.write_sheet("sheets", sheets)
		wt.end_write()
		wt.close()

		converter = exporter.find_converter(info["parser"])
		module = DataModule(outfile, info, None, converter)
		module.sheets = sheets
		return module
