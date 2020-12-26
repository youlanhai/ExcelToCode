# -*- coding: utf-8 -*-
import traceback
import util

# 导表阶段
class BaseStage(object):

	@property
	def need_sort(self): return False

	def __init__(self, info):
		self.info = info

	def get_desc(self): return "导表阶段: " + str(type(self))

	def process(self, exporter):
		self.exporter = exporter

		data_modules = exporter.data_modules
		keys = list(data_modules.keys())
		if self.need_sort:
			keys.sort()

		for key in keys:
			data_module = data_modules[key]
			error = None
			try:
				self.process_sheet(data_module)
			except util.ExcelToCodeException as e:
				error = e
			except Exception as e:
				traceback.print_exc()
				error = e

			if error:
				util.log_error(e, file = key)

		return

	def process_sheet(self, data_module):
		raise RuntimeError("该方法未实现")
