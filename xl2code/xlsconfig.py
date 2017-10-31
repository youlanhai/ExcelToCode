# -*- coding: utf-8 -*-

######################################################################
### 导表阶段。可以控制writer在哪个阶段输出写文件
######################################################################
EXPORT_STAGE_RAW = 0

EXPORT_STAGE_BEGIN = 1

EXPORT_STAGE_FINAL = 2

######################################################################
###
######################################################################

# 出错后是否继续运行。常用来显示出，所有出错的地方。
FORCE_RUN = False

# 是否使用openpyxl来解析excel表。目前总是使用该插件。
USE_OPENPYXL = True

# 是否执行快速导出。仅导出修改了的excel文件。
FAST_MODE = False

# 工程路径。CONFIG_PATH是配置文件所在的路径
PROJECT_PATH = "$CONFIG_PATH"

# 默认的writer缩进
DEFAULT_INDENT = 2

# 临时文件中的writer缩进
TEMP_FILE_INDENT = 3

######################################################################
### 以下是需要配置的路径。可以通过配置文件来设置，见load_configure
######################################################################

# 导出类
EXPORTER_CLASS = "DirectExporter"

# 定制化导表阶段
# EXPORTER_STAGES = []

# Excel路径
INPUT_PATH      = "$PROJECT_PATH/excels"

# 中间文件路径
TEMP_PATH       = "$PROJECT_PATH/export/temp"

# 输出路径
OUTPUT_PATH 	= "$PROJECT_PATH/export/output"

DEFAULT_JAVA_PACKAGE = "com.mygame.default.package"

# 代码生成器
CODE_GENERATORS  = []

# 输出数据配置。
DATA_WRITERS = []

# 自定义后处理阶段。在导表最后阶段调用，能够访问到exporter的所有数据。常用于生成文件列表。
CUSTOM_STAGES = []

# python插件安装包路径。
DEPENDENCIES = {}

# Excel表头参数解析
ARGUMENT_CONVERTER = {
	"版本：" 			: ["version", "int"],
	"键值是否重复：" 	: ["multiKey", "bool"],
	"说明：" 			: ["describe", "string"],
	"模板：" 			: ["template", "string"],
	"关联总表：" 		: ["mergeToSheet", "path"],
	"合并到总表："		: ["mergeToSheet", "path"],
	"合并到文件："		: ["mergeToFile", "path"],
	"缩进：" 			: ["indent", 	"int"],
	"输出路径："		: ["outputPath", "path"],
	"常量表：" 		: ["constant", "bool"],
}

# Excel表格数据所在行。索引从0开始，不填或填-1表示该行不存在。
SHEET_ROW_INDEX = {
	# Excel表头参数。通常是版本信息和说明等，该行必须存在。
	"argument" 	: 0,
	# 表头。该行必须存在。
	"header" 	: 1,
	# 数据首行索引。该行必须存在。
	"data" 		: 2,
	# 字段。Direct模式下，该行必须存在
	"field" 	: -1,
	# 类型行。Direct模式下，该行必须存在
	"type" 		: -1,
	# 默认值所在行。如果某列没填，可以用此值替代
	"default" 	: -1,
}

#----------- ConfigExporter/MixExporter需要的参数 ---------------------#

# 转换器所在的路径。
CONVERTER_PATH  = "$PROJECT_PATH/converters"

# 转换器子目录，位于CONVERTER_PATH下。防止命名冲突。
CONVERTER_ALIAS = "converter"

# Excel与转换器对应关系表
CONVENTION_TABLE = ()

# 分表合并关系表
MERGE_TABLE = ()

#----------- ConfigExporter/MixExporter需要的参数 ---------------------#

######################################################################
### 实现下面两个函数，定制自己的初始化参数
######################################################################

# 初始化开始回调。
# @param cfg 	是xlsconfig模块，要修改参数需要修改cfg中的参数。
def pre_init_method(cfg):
	print "start init"

# 初始化完成后回调
def post_init_method(cfg):
	print "post init finished"
