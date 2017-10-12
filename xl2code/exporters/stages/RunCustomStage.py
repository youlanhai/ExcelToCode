# -*- coding: utf-8 -*-
import traceback
import xlsconfig
import util
from BaseStage import BaseStage

class RunCustomStage(BaseStage):

	def get_desc(self): return "执行自定义阶段"

	def process(self, exporter):
		from exporters import stages
		
		for stage_info in xlsconfig.CUSTOM_STAGES:
			stage_class = stages.classes.get(stage_info["class"], None)
			if stage_class is None:
				util.log_error("Failed find stage '%s'", stage_info["class"])
				break
			
			stage = stage_class(stage_info)
			print "=== %s ===" % stage.get_desc()
			stage.process(exporter)

		return
