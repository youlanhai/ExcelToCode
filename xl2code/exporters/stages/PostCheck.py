# -*- coding: utf-8 -*-
import traceback
import util
from BaseStage import BaseStage

class PostCheck(BaseStage):

	def get_desc(self): return "数据合法性检查"

	def post_check_sheet(self, data_module):
		converter = data_module.converter
		if converter is None: return

		check_method = getattr(converter, "post_check", None)
		if check_method is None:
			return

		try:
			check_method(data_module, self)
		except:
			traceback.print_exc()
			util.log_error("数据检查失败 '%s'", data_module.path)

		return
