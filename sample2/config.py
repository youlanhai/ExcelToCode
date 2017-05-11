# -*- coding: utf-8 -*-

# 导出模式
EXPORTER_CLASS = "ConfigExporter"

# 表头行索引
SHEET_ROW_INDEX = {
	"argument" : 0,
	"header" : 1,
	"data" : 2,
}

# Excel输入路径
INPUT_PATH = "excels"

# 中间文件存放路径
TEMP_PATH = "export/xtemp"

# 转换器父级路径
CONVERTER_PATH = "converters"

# 转换器子目录，转换器脚本存放在这里。目的是防止命名冲突
CONVERTER_ALIAS = "converter"

# 默认Java包名。用于生成Java代码用
DEFAULT_JAVA_PACKAGE = "com.mygame.excel"

# 代码生成器
CODE_GENERATORS = [
	{
		"class" : "JavaCodeGen",
		"name_format" : "Dict%s",
		"file_path" : "export/java/code",
		"imports" : ["com.mygame.test"],
		"interface" : "IInterface",
		"base" : "BaseClass",
	}
]

# 数据输出器
DATA_WRITERS = [
	{"stage" : 1, "class" : "JavaWriter", "file_path": "export/java/data", "file_posfix" : ".wg"},
	{"stage" : 2, "class" : "PyWriter", "file_path": "export/python", "file_posfix" : ".py"},
]
