# -*- coding: utf-8 -*-
import traceback
import util
from BaseStage import BaseStage

class PostProcess(BaseStage):

	def get_desc(self): return "后处理数据"

	def process_sheet(self, data_module):
		converter = data_module.converter
		if converter is None: return

		process_method = getattr(converter, "post_process", None)
		if process_method is None:
			return

		try:
			data_module.extra_sheets = process_method(data_module)
		except:
			traceback.print_exc()
			util.log_error("脚本处理失败 '%s'", data_module.path)

		return
