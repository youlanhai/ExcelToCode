# -*- coding: utf-8 -*-
import os
import xlsconfig
import util
import writers
from BaseStage import BaseStage

class WriteFileList(BaseStage):

	def get_desc(self): return "写入文件列表"

	def process(self, export):
		sheet = {}
		for k, v in export.data_modules.iteritems():
			sheet[k] = v.info["parser"]

		full_path = os.path.join(xlsconfig.TEMP_PATH, "files.py")
		util.ensure_folder_exist(full_path)

		wt = writers.PyWriter(full_path, None)
		wt.max_indent = xlsconfig.TEMP_FILE_INDENT
		wt.begin_write()
		wt.write_sheet("main_sheet", sheet)
		wt.end_write()
		wt.close()
		return
