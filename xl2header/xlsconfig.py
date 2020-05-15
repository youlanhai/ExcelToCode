# -*- coding: utf-8 -*-

# Excel表头参数解析
ARGUMENT_CONVERTER = {
	"版本" 			: ["version", "int"],
	"键值是否重复" 	: ["multiKey", "bool"],
	"说明" 			: ["describe", "string"],
	"模板" 			: ["template", "string"],
	"关联总表" 		: ["mergeToSheet", "path"],
	"合并到总表"		: ["mergeToSheet", "path"],
	"合并到文件"		: ["mergeToFile", "path"],
	"缩进" 			: ["indent", "int"],
	"输出路径"		: ["outputPath", "path"],
	"常量表" 		: ["constant", "bool"],
	"垂直排列" 		: ["vertical", "bool"],
	"存在默认行"		: ["existDefaultRow", "bool"],
}

# Excel表格数据所在行。索引从0开始，不填或填-1表示该行不存在。
SHEET_ROW_INDEX = {
	# Excel表头参数。通常是版本信息和说明等，该行必须存在。
	"argument" 	: 0,
	# 表头。该行必须存在。
	"header" 	: 2,
	# 字段。Direct模式下，该行必须存在
	"field" 	: 3,
	# 类型行。Direct模式下，该行必须存在
	"type" 		: 4,
	# 数据首行索引。该行必须存在。
	"data" 		: 5,
	# 默认值所在行。如果某列没填，可以用此值替代
	"default" 	: -1,
	# 如果是垂直排列的话，从第几行开始才是真正的数据
	"verticalStartRow" : 2,
}
