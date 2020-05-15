# -*- coding: utf-8 -*-

class Header:
	def __init__(self):
		self.title = None
		self.field = None
		self.field_type = None
		self.type = None
		self.children = []

	@property
	def is_list(self):
		return self.type == "list"

	@property
	def is_dict(self):
		return self.type == "dict"

	@property
	def is_normal(self):
		return self.type is None or self.type == "normal"

	def load(self, file_path):
		pass

	def save(self, file_path):
		pass

	def merge(self, other):
		pass

	def find_child(self, title):
		for child in self.children:
			if child.title == title:
				return child
		return None
