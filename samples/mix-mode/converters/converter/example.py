# -*- coding: utf-8 -*-
from tps import tp0

KEY_NAME = "ID"

CONFIG = [
	("掉落关卡", "drops", tp0.to_int_list, True),
]

# 添加此函数，在导表结束之前可以做一些后处理
def post_process(data_module):
	pass

# 添加此函数，用于在导表结束之后进行一些数据合法性检查
def post_check(data_module, exporter):
	pass
