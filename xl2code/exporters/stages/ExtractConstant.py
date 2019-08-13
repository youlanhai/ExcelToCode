# -*- coding: utf-8 -*-
import traceback
import util
from BaseStage import BaseStage

class ExtractConstant(BaseStage):

	def get_desc(self): return "提取常量数据"

	def process_sheet(self, data_module):
		sheet = data_module.main_sheet
		if not data_module.info["arguments"].get("constant"):
			return

		data_module.main_sheet = None
		if len(sheet) > 0:
			no = min(sheet.iterkeys())
			data_module.constants = sheet[no]

		return
