# -*- coding: utf-8 -*-
from BaseStage import BaseStage

# 解析Excel表
class ParseExcel(BaseStage):

	def get_desc(self): return "解析Excel表"

	def process(self, exporter):
		exporter.gather_excels()

		# export excels to temp python
		exporter.export_excels()
