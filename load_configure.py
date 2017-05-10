# -*- coding: utf-8 -*-
import os
import json
import sys
import imp

import xlsconfig
from util import to_utf8

######################################################################
### 加载配置文件。cfg_file是json格式的文件。
### 注意，json中读取出来的字符串格式都是unicode，路径需要转换成utf-8格式。
######################################################################
def load_configure(cfg_file):
	cfg_file = os.path.abspath(cfg_file)
	print "load configure file", cfg_file

	cfg = None
	with open(cfg_file, "r") as f:
		cfg = json.load(f, "utf-8")

	root_path = os.path.dirname(cfg_file)

	xlsconfig.PROJECT_PATH = root_path

	xlsconfig.EXPORTER_CLASS = cfg["EXPORTER_CLASS"]

	xlsconfig.SHEET_ROW_INDEX = cfg["SHEET_ROW_INDEX"]

	xlsconfig.INPUT_PATH = join_path(root_path, to_utf8(cfg["INPUT_PATH"]))

	xlsconfig.TEMP_PATH = join_path(root_path, to_utf8(cfg.get("TEMP_PATH", "temp")))

	xlsconfig.CONVERTER_PATH = join_path(root_path, to_utf8(cfg.get("CONVERTER_PATH", "converters")))
	xlsconfig.CONVERTER_ALIAS = to_utf8(cfg.get("CONVERTER_ALIAS", "converter"))

	convention_script_file = os.path.join(xlsconfig.CONVERTER_PATH, "convention_table.py")
	if os.path.exists(convention_script_file):
		convention_module = imp.load_source("custom_convention_table", convention_script_file)

		xlsconfig.CONVENTION_TABLE = getattr(convention_module, "CONVENTION_TABLE", ())
		xlsconfig.MERGE_TABLE = getattr(convention_module, "MERGE_TABLE", ())

	val = cfg.get("ARGUMENT_CONVERTER", None)
	if val: xlsconfig.ARGUMENT_CONVERTER = val

	xlsconfig.CODE_GENERATORS = cfg.get("CODE_GENERATORS", ())
	for info in xlsconfig.CODE_GENERATORS:
		info["file_path"] = join_path(root_path, to_utf8(info["file_path"]))

	xlsconfig.DATA_WRITERS = cfg.get("DATA_WRITERS", ())
	for info in xlsconfig.DATA_WRITERS:
		info["file_path"] = join_path(root_path, to_utf8(info["file_path"]))

	xlsconfig.DEPENDENCIES = cfg.get("DEPENDENCIES", {})
	for k in xlsconfig.DEPENDENCIES.keys():
		path = xlsconfig.DEPENDENCIES[k]
		xlsconfig.DEPENDENCIES[k] = join_path(root_path, path)

	xlsconfig.POSTPROCESSORS = cfg.get("POSTPROCESSORS", ())
	for info in xlsconfig.POSTPROCESSORS:
		info["file_path"] = join_path(root_path, to_utf8(info["file_path"]))

	# 加载完毕回调
	post_init_script = cfg.get("POST_INIT_SCRIPT")
	if post_init_script:
		path = join_path(root_path, post_init_script)
		imp.load_source("custom_post_init_script", path)

	xlsconfig.DEFAULT_JAVA_PACKAGE = to_utf8(cfg.get("DEFAULT_JAVA_PACKAGE"))

	return

def join_path(*args):
	return os.path.normpath(os.path.join(*args))
