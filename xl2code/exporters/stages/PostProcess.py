# -*- coding: utf-8 -*-
import traceback
import util
from BaseStage import BaseStage

class PostProcess(BaseStage):

	def get_desc(self): return "后处理数据"

	def process_sheet(self, data_module):
		converter = data_module.converter
		if converter is None:
			return

		process_method = getattr(converter, "post_process_ex", None)
		if process_method:
			try:
				data_module.extra_sheets = process_method(data_module, self.exporter)
			except:
				traceback.print_exc()
				util.log_error("脚本后处理失败", file = data_module.path)
			return

		process_method = getattr(converter, "post_process", None)
		if process_method:
			try:
				data_module.extra_sheets = process_method(data_module)
			except:
				traceback.print_exc()
				util.log_error("脚本后处理失败", file = data_module.path)

		return
