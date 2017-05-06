# -*- coding: utf-8 -*-
from base_writer import BaseWriter
from xlsparser import intToBase26
from copy import copy

IndentChar = '\t'
Indents = [IndentChar * i for i in xrange(1, 10)]

class LuaWriter(BaseWriter):

	def begin_write(self):
		output = self.output

		module_info = self.data_module.info

		self.write_comment("key = %s" % module_info["key_name"])

		sheet_types = copy(module_info["sheet_types"]["main_sheet"])
		sheet_types.sort(key = lambda v : v[0])
		for info in sheet_types:
			col, field, text, type = info
			col_name = intToBase26(col) if col is not None else "None"
			comment = "%s\t%-20s%s" %(col_name, field, text)
			self.write_comment(comment)

		output("\n")

		output("local _G = _G\n")
		output("local module_name = ...\n")
		output("module(module_name)\n\n")

	def end_write(self):
		pass
		# output = self.output
		# output("_G.print('model loaded:', module_name)\n")


	def write_sheet(self, name, sheet, maxIndent = 1):
		output = self.output

		output(name)
		output(" = {\n")

		keys = sheet.keys()
		keys.sort()

		key_format = "\t[%d] = "
		if len(keys) > 0 and isinstance(keys[0], basestring):
			key_format = "\t[\"%s\"] = "

		for k in keys:
			output(key_format % k)
			self.write(sheet[k], 1, maxIndent)
			output(",\n")

			self.flush()

		output("}\n\n")

		if name == "main_sheet":
			self.write_value("main_length", len(sheet))

			keys = sheet.keys()
			keys.sort()
			self.write_value("main_keys", keys)

		self.flush()

	def write_value(self, name, value):
		output = self.output

		output(name)
		output(" = ")
		self.write(value)
		output("\n\n")

		self.flush()

	def write_comment(self, comment):
		self.output("-- ")
		self.output(comment)
		self.output("\n")

	def write(self, value, indent = 0, maxIndent = 0):
		output = self.output

		if value is None:
			return output("nil")

		tp = type(value)
		if tp == bool:
			output("true" if value else "false")

		elif tp == int:
			output("%d" % (value, ))

		elif tp == float:
			output("%g" % (value, ))

		elif tp == str:
			output('"%s"' %(value, ))

		elif tp == unicode:
			output('"%s"' % (value.encode("utf-8"), ))

		elif tp == tuple or tp == list or tp == set or tp == frozenset:
			output("{")
			indent += 1
			for v in value:
				self.write_indent(indent, maxIndent)
				self.write(v, indent, maxIndent)
				output(", ")
			indent -= 1
			if len(value) > 0 and indent + 1 <= maxIndent:
				self.write_indent(indent, maxIndent)
			output("}")

		elif tp == dict:
			output("{")
			indent += 1

			keys = value.keys()
			keys.sort()
			for k in keys:
				self.write_indent(indent, maxIndent)
				output("[")
				self.write(k, 0, 0)
				output("] = ")
				self.write(value[k], indent, maxIndent)
				output(", ")

			indent -= 1
			if len(value) > 0 and indent + 1 <= maxIndent:
				self.write_indent(indent, maxIndent)
			output("}")

		else:
			raise TypeError, "unsupported type %s" % (str(tp), )

		return

	def write_indent(self, indent, maxIndent):
		if indent <= maxIndent:
			self.output("\n")
			self.output(Indents[indent])
