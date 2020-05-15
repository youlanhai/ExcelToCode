# -*- coding: utf-8 -*-
import re
import copy

SPLITER_PATTERN = re.compile(r"\[|\{|\]|\}")

class MergeField:
	def __init__(self, header_list):
		self.header_list = header_list
		self.fields = None

	def merge_fields(self):
		parent = {
			"values" : [],
			"dict": True,
		}
		self.fields = parent
		last_field = ""
		for field, header in self.iter_fields(self.header_list):
			print "merge_fields", field

			if field == '{':
				value = copy.copy(header)
				value["parent"] = parent
				value["values"] = []
				value["tp"] = "dict"
				value["field"] = last_field

				if last_field:
					parent["values"].pop()

				self.add_value(parent, value)
				parent = value
				last_field = ""

			elif field == '}':
				parent["end"] = header["title"]
				parent = parent.pop("parent")
				last_field = ""

			elif field == '[':
				value = copy.copy(header)
				value["parent"] = parent
				value["values"] = []
				value["tp"] = "list"
				value["field"] = last_field

				if last_field:
					parent["values"].pop()

				self.add_value(parent, value)
				parent = value
				last_field = ""

			elif field == ']':
				parent["end"] = header["title"]
				parent = parent.pop("parent")
				last_field = ""

			else:
				value = copy.copy(header)
				value["field"] = field
				self.add_value(parent, value)
				last_field = field

	def to_list(self):
		self.header_list = []
		self.headers = {}

		self.fields_to_list(self.fields)

		ret = []
		for header in self.header_list:
			ret.append("%s,%s,%s" % (header["title"], header["field"], header["type"]))
		return "\n".join(ret)

	def fields_to_list(self, fields):
		for value in fields["values"]:
			title = value["title"]
			exist_value = self.headers.get(title)
			if exist_value:
				exist_value["field"] += value["field"]
				exist_value["type"] = value["type"]
				exist_value["tp"] = value.get("tp")
				exist_value["values"] = value.get("values")
				value = exist_value
			else:
				self.headers[title] = value
				self.header_list.append(value)

			tp = value.get("tp")
			if tp == "list":
				value["field"] = value["field"] + '['
				self.fields_to_list(value)
				value.pop("values", None)

				if value["end"] in self.headers:
					self.header_list[-1]["field"] += "]"
				else:
					node = copy.copy(value)
					node["title"] = node["end"]
					node["field"] = "]"
					self.header_list.append(node)

			elif tp == "dict":
				value["field"] = value["field"] + '{'
				self.fields_to_list(value)
				value.pop("values", None)

				if value["end"] in self.headers:
					self.header_list[-1]["field"] += "}"
				else:
					node = copy.copy(value)
					node["title"] = node["end"]
					node["field"] = "}"
					self.header_list.append(node)
		return

	@staticmethod
	def add_value(node, value):
		node["values"].append(value)

	@staticmethod
	def iter_fields(headers):
		for header in headers:
			field = header["field"]

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
