# -*- coding: utf-8 -*-
import os
import sys
import imp

import xlsconfig
import util
from util import resolve_path, ExcelToCodeException

######################################################################
### 加载配置文件。cfg_file是python格式的文件。
######################################################################
def load_configure(cfg_file, option):
	cfg_file = os.path.abspath(cfg_file)
	util.log("load configure file", cfg_file)

	if not os.path.exists(cfg_file):
		raise ExcelToCodeException, "配置文件不存在: %s" % cfg_file

	cfg_path = os.path.dirname(cfg_file)
	sys.path.insert(0, cfg_path)

	cfg = imp.load_source("custom_configure", cfg_file)
	for k, v in cfg.__dict__.iteritems():
		if k.startswith('_'): continue

		setattr(xlsconfig, k, v)

	file_path = os.path.dirname(cfg_file)
	xlsconfig.CONFIG_PATH = file_path

	module_path = os.path.dirname(os.path.abspath(__file__))
	xlsconfig.TOOL_PATH = os.path.dirname(module_path)

	xlsconfig.pre_init_method(xlsconfig)

	safe_parse_path(option, "project", "PROJECT_PATH")
	safe_parse_path(option, "input", "INPUT_PATH")
	safe_parse_path(option, "output", "OUTPUT_PATH")
	safe_parse_path(option, "temp", "TEMP_PATH")
	safe_parse_path(option, "converter", "CONVERTER_PATH")
	safe_parse_path(option, "locale_path", "LOCALE_OUTPUT_PATH")


	for k in xlsconfig.DEPENDENCIES.keys():
		path = xlsconfig.DEPENDENCIES[k]
		xlsconfig.DEPENDENCIES[k] = resolve_path(path)

	names = (
		"CSV_CONVERTER",
	)
	for name in names:
		value = resolve_path(getattr(xlsconfig, name))
		setattr(xlsconfig, name, value)

	# 所有已知的配置中，名字叫'file_path'的路径，会自动转义

	# resolve_path_in_config(xlsconfig.CODE_GENERATORS)
	# resolve_path_in_config(xlsconfig.DATA_WRITERS)
	# resolve_path_in_config(xlsconfig.CUSTOM_STAGES)

	# 加载完毕回调
	xlsconfig.post_init_method(xlsconfig)
	return

# 解析并转义路径
# option中的路径参数优先于配置文件中的参数
def safe_parse_path(option, option_key, cfg_key):
	path = getattr(option, option_key, None)
	if path is None:
		path = getattr(xlsconfig, cfg_key)

	path = resolve_path(path)
	setattr(xlsconfig, cfg_key, path)

# 转义所有后缀为'_path'的变量
def resolve_path_in_config(config):
	for info in config:
		keys = info.keys()
		for k in keys:
			if k.endswith("_path"):
				info[k] = resolve_path(info[k])

	return
