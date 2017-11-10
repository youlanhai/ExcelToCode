# -*- coding: utf-8 -*-

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
		if self.need_sort:
			keys = data_modules.keys()
			keys.sort()
			for key in keys:
				data_module = data_modules[key]
				self.process_sheet(data_module)
		else:
			for data_module in data_modules.itervalues():
				self.process_sheet(data_module)

		return

	def process_sheet(self, data_module):
		pass
