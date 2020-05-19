# -*- coding: utf-8 -*-
import re
from header import Header, Argument
import util

SPLITER_PATTERN = re.compile(r"\[|\{|\]|\}")

def gen_header_tree(list_root, filename = ""):
	root = Header.new_root()

	last_field = ""
	parent = root
	indent = 0
	for field, header in lex_fields(list_root.children):
		print "merge_fields", field

		if field == '{' or field == '[':
			value = header.clone()
			value.parent = parent
			value.children = []
			value.type = field
			value.field = last_field

			if last_field:
				parent.children.pop()

			parent.add_child(value)
			parent = value
			last_field = ""
			indent += 1

		elif field == '}' or field == ']':
			parent.end_title = header.title
			parent.end_index = header.index
			parent = parent.parent
			last_field = ""
			indent -= 1

		else:
			value = header.clone()
			value.field = field
			parent.add_child(value)
			last_field = field

	if indent != 0:
		raise util.ExcelToCodeException("括号不匹配", filename)
	return root

def lex_fields(header_list):
	for header in header_list:
		field = header.field

		while len(field) > 0:
			spliter = SPLITER_PATTERN.search(field)
			if spliter is None:
				yield (field, header)
				break

			split_pos = spliter.start()
			if split_pos > 0:
				yield (field[0:split_pos].strip(), header)

			yield (field[split_pos], header)

			field = field[split_pos + 1:].strip()
	return

def gen_header_list(tree):
	root = Header.new_root()
	tree_to_list(tree.children, root)
	return root

	# ret = []
	# for header in root.children:
	# 	ret.append("%s,%s,%s" % (header["title"], header["field"], header["type"]))
	# return "\n".join(ret)

def tree_to_list(children, root):
	for child in children:
		node = root.find_child(child.title)
		if node:
			# 存在同名的结点。直接修改参数，合并field名称
			node.field += child.field
			node.field_type = child.field_type
			node.index = child.index
		else:
			# 克隆一份出来，不影响原始数据
			node = Header()
			node.title = child.title
			node.field = child.field
			node.field_type = child.field_type
			node.index = child.index
			root.add_child(node)

		if child.type is None:
			continue

		# type is '{' or '['
		node.field += child.type
		tree_to_list(child.children, root)

		end_mark = '}' if child.type == '{' else ']'

		if root.find_child(child.end_title):
			root.children[-1].field += end_mark
		else:
			# 为结束符增加一个新结点
			node = Header()
			node.title = child.end_title
			node.field = end_mark
			node.field_type = child.field_type
			node.index = child.end_index
			root.add_child(node)
	return


# arguments和表头内容的分隔符。需要至少10个‘=’
SPLITER = "==========================================="

def save_header_list(file_path, root, arguments):
	with open(file_path, "wb") as f:
		for key, value in arguments.values:
			f.write("%s, %s\n" % (key, value))

		f.write(SPLITER)
		f.write('\n')

		for child in root.children:
			f.write("%s, %s, %s\n" % (child.title, child.field, child.field_type))

def load_header_list(file_path):
	content = None
	with open(file_path, "r") as f:
		content = f.read()

	arguments = Argument()
	match = re.search(r"==========*", content)
	if match:
		argument_content = content[:match.start()]
		content = content[match.end():]

		for line in argument_content.split('\n'):
			line = line.strip()
			if len(line) == 0:
				continue

			values = line.split(',')
			key = values[0].strip()
			value = values[1].strip()
			arguments.add(key, value)

	root = Header.new_root()
	for line in content.split('\n'):
		line = line.strip()
		if len(line) == 0:
			continue

		values = line.split(',')
		node = Header()
		node.title = values[0].strip()
		node.field = values[1].strip()
		node.field_type = values[2].strip() if len(values) >= 3 else "empty"
		root.add_child(node)
	return root, arguments
