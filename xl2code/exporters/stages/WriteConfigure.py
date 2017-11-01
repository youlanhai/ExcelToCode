# -*- coding: utf-8 -*-
import os
import xlsconfig
import util
import writers
from BaseStage import BaseStage

class WriteConfigure(BaseStage):

	def get_desc(self): return "写入表头配置参数"

	def process(self, exporter):
		output_path = os.path.join(xlsconfig.TEMP_PATH, "configures.py")

		wt = writers.PyWriter(output_path, None)
		wt.max_indent = xlsconfig.TEMP_FILE_INDENT
		wt.begin_write()

		sheet = {}
		for k, v in exporter.configures.iteritems():
			sheet[k] = {"types" : v.types, "arguments" : v.arguments }
		wt.write_sheet("configures", sheet)

		wt.write_value("merges", exporter.merge_patterns)

		wt.write_value("mergeFiles", exporter.merge_file_patterns)

		wt.end_write()
		wt.close()

