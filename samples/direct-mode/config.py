#-*- coding: utf-8 -*-

# 导出模式
EXPORTER_CLASS = "DirectExporter"

# Excel数据行索引（从0开始）
SHEET_ROW_INDEX = {
	# 表格参数
	"argument" 	: 0,
	# 表头
	"header" 	: 2,
	# 代码成员变量名
	"field" 	: 3,
	# 默认值
	"default" 	: 4,
	# 变量类型
	"type" 		: 5,
	# 数据起始行
	"data" 		: 6
}

# Excel输入路径
INPUT_PATH  = "excels"

# 中间文件存放路径
TEMP_PATH = "export/xtemp"

# 默认Java包名。用于生成Java代码用
DEFAULT_JAVA_PACKAGE = "com.mygame.excel"

# python 插件安装包路径
DEPENDENCIES = {
	"openpyxl" : "openpyxl-2.4.4.zip"
}

# 代码生成器
CODE_GENERATORS = [
	{
		"class" : "JavaCodeGen", # Java代码生成器
		"name_format" : "Dict%s",
		"file_path" : "export/java/code",
		"imports" : ["com.mygame.test"],
		"interface" : "IInterface",
		"base" : "BaseClass"
	}
]

# 输出数据
DATA_WRITERS = [
	# Java专用json数据格式
	{"stage" : 1, "class" : "JavaWriter", "file_path": "export/java/data", "file_posfix" : ".wg"},
]

# 后处理器
POSTPROCESSORS = [
	# 生成Java文件列表。Json格式
	{
		"class" : "JavaFileListProcessor",
		"file_path": "export/java/data/files.wg",
		"class_name_format" : "Dict%s",
		"enum_name_format" : "Files.%s"
	},
	# 生成Java枚举类，列举了所有文件。
	{
		"class" : "JavaFileEnumProcessor",
		"file_path": "export/java/code/Files.java"
	}
]

# 自定义的初始化函数
def post_init_method():
	print "自定义初始化完毕"
