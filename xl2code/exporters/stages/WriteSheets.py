# -*- coding: utf-8 -*-
import os
import xlsconfig
import util
import writers
from BaseStage import BaseStage

class WriteSheets(BaseStage):

	def __init__(self, info):
		super(WriteSheets, self).__init__(info)
		self.stage = info["stage"]

	def get_desc(self): return "保存阶段[%d]数据" % self.stage

	def process(self, export):
		data_modules = export.data_modules

		for writer_info in xlsconfig.DATA_WRITERS:
			if writer_info["stage"] != self.stage: continue

			for data_module in data_modules.itervalues():
				outfile = data_module.info["outfile"]
				self.write_one_sheet(writer_info, outfile, data_module)
		return

	def write_one_sheet(self, writer_info, outfile, data_module):
		writer_name = writer_info["class"]

		ns = {
			"FILE_PATH" : outfile,
			"FILE_DIR" : os.path.dirname(outfile),
			"FILE_NAME" : os.path.basename(outfile),
		}
		full_path = util.resolve_path(writer_info["file_path"], (ns, xlsconfig, ))
		util.ensure_folder_exist(full_path)

		writer_class = getattr(writers, writer_name)
		wt = writer_class(full_path, data_module, writer_info)
		wt.write_comment("此文件由导表工具自动生成，禁止手动修改。")
		wt.write_comment("from " + data_module.info["infile"])

		wt.begin_write()
		wt.write_sheet("main_sheet", data_module.main_sheet)

		extra_sheets = getattr(data_module, "extra_sheets", None)
		if extra_sheets is not None:
			assert(isinstance(extra_sheets, dict))
			wt.write_module(extra_sheets)

		wt.end_write()
		wt.close()
		return
