# -*- coding: utf-8 -*-

# 导表阶段
class BaseStage(object):

	def __init__(self, info):
		self.info = info

	def get_desc(self): return "导表阶段: " + str(type(self))

	def process(self, exporter):
		self.exporter = exporter

		for data_module in exporter.data_modules.itervalues():
			self.process_sheet(data_module)

		return

	def process_sheet(self, data_module):
		pass
