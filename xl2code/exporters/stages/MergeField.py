# -*- coding: utf-8 -*-
import re
import util
from BaseStage import BaseStage

class NodeBase:
	def __init__(self, key):
		self.key = key

	def apply(self, nodes, value): pass
	def set(self, key, value): pass

class NodeNormal(NodeBase):
	def apply(self, nodes, value):
		if self.key != "" and value is not None:
			nodes[-1].set(nodes, self.key, value)

class NodeDictPush(NodeBase):
	def apply(self, nodes, value):
		self.data = {}
		nodes.append(self)

	def set(self, nodes, key, value):
		self.data[key] = value

class NodeListPush(NodeBase):
	def apply(self, nodes, value):
		self.data = []
		nodes.append(self)

	def set(self, nodes, key, value):
		self.data.append(value)

class NodePop(NodeNormal):
	def apply(self, nodes, value):
		NodeNormal.apply(self, nodes, value)

		node = nodes.pop()
		if len(node.data) > 0:
			nodes[-1].set(nodes, node.key, node.data)

class NodeRoot(NodeBase):
	def begin(self):
		self.data = {}
		self.nodes = [self, ]

	def end(self):
		if len(self.nodes) != 1:
			util.log_error("key = %s, 缺少结束括号", self.key)
		data = self.data
		self.data = None
		self.nodes = None
		return data

	def set(self, nodes, key, value):
		self.data[key] = value


FIELD_NODE_MAP = {
	"-" : NodeNormal,
	'[' : NodeListPush,
	'{' : NodeDictPush,
	']' : NodePop,
	'}' : NodePop,
}

spliter_pattern = re.compile(r"\[|\{|\]|\}")

class TypeDescriptor:
	def __init__(self, field):
		spliter = spliter_pattern.search(field)
		self.child = None
		if spliter:
			split_pos = spliter.start()
			self.mode = field[split_pos]
			self.key = field[:split_pos].strip()

			if split_pos + 1 < len(field):
				self.child = TypeDescriptor(field[split_pos + 1:])
		else:
			self.key = field.strip()
			self.mode = "-"

		self.node = FIELD_NODE_MAP[self.mode](self.key)

	def apply(self, nodes, value):
		self.node.apply(nodes, value)
		if self.child:
			self.child.apply(nodes, value)

		return


class MergeField(BaseStage):

	def get_desc(self): return "合并字段"

	def process_sheet(self, data_module):
		sheet = data_module.main_sheet
		types = data_module.info["sheet_types"]["main_sheet"]
		multi_key = data_module.info["arguments"].get("multiKey", False)
		try:
			self.convert_sheet(sheet, types, multi_key)
		except Exception, e:
			util.log(e)
			util.log_error("处理字段失败，%s", data_module.path)

	def convert_sheet(self, sheet, types, multi_key):
		col2type = {}
		for type_info in types.itervalues():
			col = type_info[0]
			col2type[col] = TypeDescriptor(type_info[1])

		for key in sheet.keys():
			row = sheet[key]
			ret = None
			try:
				if multi_key:
					ret = []
					for sub_row in row:
						ret.append(self.convert_field_row(col2type, key, sub_row))
				else:
					ret = self.convert_field_row(col2type, key, row)
				sheet[key] = ret
			except Exception, e:
				util.log("处理字段失败", key)
				raise e
		return

	def convert_field_row(self, col2type, key, row):
		root = NodeRoot(key)
		root.begin()

		for col, value in enumerate(row):
			type_desc = col2type.get(col)
			if type_desc is None:
				continue

			type_desc.apply(root.nodes, value)

		return root.end()
