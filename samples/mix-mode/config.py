# -*- coding: utf-8 -*-

# 导出模式
EXPORTER_CLASS = "MixExporter"

# 数据行索引
SHEET_ROW_INDEX = {
	"argument" : 0,
	"header" : 2,
	"field" : 3,
	"type" : 4,
	"data" : 5
}

# Excel输入路径
INPUT_PATH  = "$CONFIG_PATH/excels"

OUTPUT_PATH = "$CONFIG_PATH/output"

# 中间文件存放路径
TEMP_PATH = "$OUTPUT_PATH/xtemp"

# 转换器父级路径
CONVERTER_PATH = "$CONFIG_PATH/converters"

# 转换器子目录，转换器脚本存放在这里。目的是防止命名冲突
CONVERTER_ALIAS = "converter"

# 默认Java包名。用于生成Java代码用
DEFAULT_JAVA_PACKAGE = "com.mygame.excel"


# 配置文件是python格式，所以也支持自定义变量
java_output_path = "$OUTPUT_PATH/java/"

# 代码生成器
CODE_GENERATORS = [
	{
		"class" : "JavaCodeGen", # Java代码生成器
		"name_format" : "Dict%s",
		"file_path" : java_output_path + "code/${FILE_PATH}.java",
		"imports" : ["com.mygame.test"],
		"interface" : "IInterface",
		"base" : "BaseClass"
	}
]

# 输出数据
DATA_WRITERS = [
	# Java专用json数据格式
	{"stage" : 1, "class" : "JavaWriter", "file_path": java_output_path + "data/${FILE_PATH}.wg"},
	# Python数据表
	{"stage" : 2, "class" : "PyWriter", "file_path": "$OUTPUT_PATH/python/${FILE_DIR}/d_${FILE_NAME}.py"},
]

# 后处理器
POSTPROCESSORS = [
	# 生成Java文件列表。Json格式
	{
		"class" : "JavaFileListProcessor",
		"file_path": java_output_path + "data/files.wg",
		"class_name_format" : "Dict%s",
	},
	# 生成Java枚举类，列举了所有文件。
	{
		"class" : "JavaFileEnumProcessor",
		"file_path": java_output_path + "code/Files.java"
	}
]
