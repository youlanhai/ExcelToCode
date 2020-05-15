# -*- coding: utf-8 -*-

class Header:
	def __init__(self):
		self.title = ""
		self.field = ""
		self.field_type = ""
		self.type = None
		self.index = 0
		self.end_title = ""
		self.end_index = 0
		self.children = None
		self.parent = None

	@classmethod
	def new_root(cls):
		node = cls()
		node.title = "root"
		node.type = '{'
		node.children = []
		return node

	@property
	def is_list(self):
		return self.type == "["

	@property
	def is_dict(self):
		return self.type == "{"

	@property
	def is_normal(self):
		return self.type is None or self.type == "normal"

	def copy_from(self, h):
		self.title = h.title
		self.field = h.field
		self.field_type = h.field_type
		self.type = h.type
		self.index = h.index
		self.end_index = h.end_index
		self.end_title = h.end_title

	def clone(self):
		ret = Header()
		ret.copy_from(self)
		return ret

	def find_child(self, title):
		for child in self.children:
			if child.title == title:
				return child
		return None

	def add_child(self, child):
		self.children.append(child)
