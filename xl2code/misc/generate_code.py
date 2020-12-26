# -*- coding: utf-8 -*-
import os
import imp
import xlsconfig
import util

import codegen

def generate_code():
	util.log("=== 生成代码类文件 ...")

	configure_file_path = os.path.join(xlsconfig.TEMP_PATH, "configures.py")
	if not os.path.exists(configure_file_path):
		return util.log_error("配置文件'%s'不存在", configure_file_path)

	configure_module = imp.load_source("temp_configures", configure_file_path)

	for key, cfg in configure_module.configures.items():
		_generate(cfg["types"], key)

def _generate(config, module_name):
	for generator_info in xlsconfig.CODE_GENERATORS:
		cls = getattr(codegen, generator_info["class"])

		gen = cls(config, module_name, generator_info)
		gen.run()
