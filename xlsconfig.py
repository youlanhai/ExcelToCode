# -*- coding: utf-8 -*-

######################################################################
### 导表阶段
######################################################################
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
CODE_GENERATORS  = [
	{"class" : "JavaCodeGen", "file_path" : "export/java/code"}
]

# 输出数据配置。
DATA_WRITERS = [
	{"stage" : EXPORT_STAGE_FINAL, "class" : "LuaWriter", "file_path": "export/lua", "file_posfix" : ".lua"},
]

# 额外的初始化脚本。
POST_INIT_SCRIPT = ""

# python插件依赖项
DEPENDENCIES = {}

# Excel与转换器对应关系表
CONVENTION_TABLE = ()

# 分表合并关系表
MERGE_TABLE = ()

######################################################################
###
######################################################################
