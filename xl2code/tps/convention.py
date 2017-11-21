# -*- coding: utf-8 -*-

# 通用类型转换关系。可通过扩展转换表，来支持自定义的类型。

import tp0
from tps import TYPE_MODULES

#: 类型转换函数映射为名称
FUNCTION_2_TYPE = {}

_FUNCTION_2_TYPE = {
	int 	: "int",
	long 	: "long",
	float 	: "float",
	bool 	: "boolean",
	tp0.to_int 	: "int",
	tp0.to_float : "float",
	tp0.to_bool : "boolean",
	tp0.to_str : "String",
	tp0.to_int_list : "Array<int>",
	tp0.to_float_list : "Array<float>",
}

def update_functions():
	global FUNCTION_2_TYPE

	fun2type = {}
	for module in TYPE_MODULES:
		for key, val in module.__dict__.iteritems():
			if key.startswith("to_"):
				fun2type[val] = key

	fun2type.update(_FUNCTION_2_TYPE)
	FUNCTION_2_TYPE = fun2type
	return

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
	name = name.lower()
	to_name = "to_" + name
	for module in TYPE_MODULES:
		fun = getattr(module, to_name, None)
		if fun is not None:
			return fun
	return TYPE_2_FUNCTION.get(name)
