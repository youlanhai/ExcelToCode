# -*- coding: utf-8 -*-
import os
import json
import sys
import imp

convention_table = None

EXPORT_STAGE_LIST = 0
EXPORT_STAGE_BEGIN = 1
EXPORT_STAGE_FINAL = 2
######################################################################
###
######################################################################

# 出错后是否继续运行。常用来显示出，所有出错的地方。
FORCE_RUN = False

# 是否使用openpyxl来解析excel表。目前总是使用该插件。
USE_OPENPYXL = True

# 是否执行完全导出。与快速导出相对立，快速导出仅会导出修改了的excel文件。
FULL_EXPORT = False

######################################################################
### 以下是需要配置的路径。可以通过配置文件来设置，见load_configure
######################################################################

# Excel路径
INPUT_PATH      = "excels"

# 导表工具依赖的插件安装包路径
DEPENDENCY_PATH = "Dependency/libs"

# 中间文件路径
TEMP_PATH       = "export/xtemp"

# 转换器所在的路径。此目录下必须有convention_table.py文件
CONVERTER_PATH  = "converters"

# 转换器子目录，位于CONVERTER_PATH下。防止命名冲突。
CONVERTER_ALIAS = "converter"

# 生成的java代码输出路径
JAVA_CODE_PATH  = "export/java/code"

# 输出数据配置。
DATA_WRITERS = [
	{"stage" : EXPORT_STAGE_FINAL, "class" : "LuaWriter", "file_path": "export/lua", "file_posfix" : ".lua"},
]

# 额外的初始化脚本。
POST_INIT_SCRIPT = ""

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
	cur_module = sys.modules[__name__]

	keys = ("INPUT_PATH", "TEMP_PATH", "CONVERTER_PATH",
		"JAVA_CODE_PATH", "DEPENDENCY_PATH")

	for key in keys:
		path = os.path.normpath(os.path.join(root_path, cfg[key].encode("utf-8")))
		print "cfg: %s = %s" % (key, path)
		setattr(cur_module, key, path)

	global CONVERTER_ALIAS, DATA_WRITERS, convention_table

	CONVERTER_ALIAS = cfg["CONVERTER_ALIAS"].encode("utf-8")

	convention_script = os.path.join(CONVERTER_PATH, "convention_table.py")
	convention_table = imp.load_source("custom_convention_table", convention_script)

	DATA_WRITERS = cfg["DATA_WRITERS"]
	for info in DATA_WRITERS:
		path = info["file_path"].encode("utf-8")
		path = os.path.normpath(os.path.join(root_path, path))
		info["file_path"] = path

	post_init_script = cfg.get("POST_INIT_SCRIPT")
	if post_init_script:
		path = os.path.normpath(os.path.join(root_path, post_init_script))
		imp.load_source("custom_post_init_script", path)

	return
