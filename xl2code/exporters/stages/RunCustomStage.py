# -*- coding: utf-8 -*-
import xlsconfig
import util
from .BaseStage import BaseStage

class RunCustomStage(BaseStage):

	def get_desc(self): return "执行自定义阶段"

	def process(self, exporter):
		from exporters import stages

		for stage_info in xlsconfig.CUSTOM_STAGES:
			stage_class = stages.CLASSES.get(stage_info["class"], None)
			if stage_class is None:
				util.log_error("Failed find stage '%s'", stage_info["class"])
				break

			stage = stage_class(stage_info)
			util.log("=== %s ===" % stage.get_desc())
			stage.process(exporter)

		return
