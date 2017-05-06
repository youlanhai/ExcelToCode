# -*- coding: utf-8 -*-
import os
import json
import sys
import imp

import xlsconfig

######################################################################
### 加载配置文件。cfg_file是json格式的文件。
######################################################################
def load_configure(cfg_file):
	cfg_file = os.path.abspath(cfg_file)
	print "load configure file", cfg_file

	cfg = None
	with open(cfg_file, "r") as f:
		cfg = json.load(f, "utf-8")

	root_path = os.path.dirname(cfg_file)

	keys = ("INPUT_PATH", "TEMP_PATH", "CONVERTER_PATH", )
	for key in keys:
		path = join_path(root_path, cfg[key].encode("utf-8"))
		print "cfg: %s = %s" % (key, path)
		setattr(xlsconfig, key, path)

	xlsconfig.CONVERTER_ALIAS = cfg["CONVERTER_ALIAS"].encode("utf-8")

	convention_script = os.path.join(xlsconfig.CONVERTER_PATH, "convention_table.py")
	convention_module = imp.load_source("custom_convention_table", convention_script)

	xlsconfig.CONVENTION_TABLE = convention_module.CONVENTION_TABLE
	xlsconfig.MERGE_TABLE = convention_module.MERGE_TABLE

	xlsconfig.CODE_GENERATORS = cfg.get("CODE_GENERATORS", {})
	for info in xlsconfig.CODE_GENERATORS:
		path = info["file_path"].encode("utf-8")
		path = join_path(root_path, path)
		info["file_path"] = path

	xlsconfig.DATA_WRITERS = cfg["DATA_WRITERS"]
	for info in xlsconfig.DATA_WRITERS:
		path = info["file_path"].encode("utf-8")
		path = join_path(root_path, path)
		info["file_path"] = path

	xlsconfig.DEPENDENCIES = cfg.get("DEPENDENCIES", {})
	for k in xlsconfig.DEPENDENCIES.keys():
		path = xlsconfig.DEPENDENCIES[k]
		xlsconfig.DEPENDENCIES[k] = join_path(root_path, path)


	# 加载完毕回调
	post_init_script = cfg.get("POST_INIT_SCRIPT")
	if post_init_script:
		path = join_path(root_path, post_init_script)
		imp.load_source("custom_post_init_script", path)

	return

def join_path(*args):
	return os.path.normpath(os.path.join(*args))
