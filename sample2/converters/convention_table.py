# -*- coding: utf-8 -*-

"""
(excel文件名正则表达式，转换器文件名称 |，新名称的正则表达式，表索引)
新名称	可以缺省，默认是原名称去除后缀
表索引	可以缺省，默认是0
eg.
缺省：(r"stage/normal/\d+/enemy.xlsx", "enemy"), -> stage/normal/\d+/enemy
改名：(r"(stage/normal/\d+/)enemy.xlsx", "enemy", r"\1d_enemy", 0), -> stage/normal/\d+/d_enemy
"""

CONVENTION_TABLE = (
	("example.xlsx", "example", ),
)

"""
合并表
excel支持分表结构，即，一个excel可以拆分成多个，每个人负责自己的部分，
导表的时候，会自动把这些子表合并到以前。MERGE_TABLE描述了合并的规则：
	(新表路径, 子表i路径, ...)
子表i的路径支持正则表达式。
"""
MERGE_TABLE = (
	("entity/entity", r"entity/entity_part\d+", ),
)
