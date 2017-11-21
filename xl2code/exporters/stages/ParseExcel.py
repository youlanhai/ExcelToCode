# -*- coding: utf-8 -*-
from BaseStage import BaseStage

# 解析Excel表
class ParseExcel(BaseStage):

	def get_desc(self): return "解析Excel表"

	def process(self, exporter):
		exporter.gather_excels()

		exporter.load_cache_file()

		# export excels to temp python
		exporter.export_excels()

		exporter.save_cache_file()
