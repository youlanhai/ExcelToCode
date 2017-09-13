# -*- coding: utf-8 -*-

# 通用类型转换关系。可通过扩展转换表，来支持自定义的类型。

import tp0

#: 类型转换函数映射为名称
FUNCTION_2_TYPE = {
	int 	: "int",
	long 	: "long",
	tp0.to_int 	: "int",
	float 	: "float",
	tp0.to_float : "float",
	tp0.to_bool : "boolean",
	bool 	: "boolean",
	tp0.to_int_list : "Array<int>",
	tp0.to_float_list : "Array<float>",
}

#: 快速转换器。将excel中的数据进行首次转换
TYPE_2_FUNCTION = {
	"byte" 		: int,
	"short" 	: int,
	"int" 		: tp0.to_int,
	"long" 		: tp0.to_int,
	"float" 	: tp0.to_float,
	"string" 	: tp0.to_str,
	"bool" 		: tp0.to_bool,
	"boolean" 	: tp0.to_bool,
	"array<int>" : tp0.to_int_list,
	"array<float>" : tp0.to_float_list,
}


def function2type(tp):
	return FUNCTION_2_TYPE.get(tp, "String")

def type2function(name):
	return TYPE_2_FUNCTION.get(name.lower(), tp0.to_str)
