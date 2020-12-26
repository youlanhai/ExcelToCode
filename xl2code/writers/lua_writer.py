# -*- coding: utf-8 -*-
from .base_writer import BaseWriter
from util import format_string

class LuaWriter(BaseWriter):

	def begin_write(self):
		super(LuaWriter, self).begin_write()

		self.array_prefix = self.generator_info.get("array_prefix", "{")
		self.array_posfix = self.generator_info.get("array_posfix", "}")

		self.dict_prefix = self.generator_info.get("dict_prefix", "{")
		self.dict_posfix = self.generator_info.get("dict_posfix", "}")

		header = self.generator_info.get("header")
		if header:
			self.output(header, "\n")

		self.output("module(...)", "\n\n")

	def write_sheet(self, name, sheet):
		self.write_value(name, sheet)

		if name == "main_sheet" and self.generator_info.get("record_keys"):
			self.write_value("main_length", len(sheet), 0)

			keys = list(sheet.keys())
			keys.sort()
			self.write_value("main_keys", keys)

		self.flush()

	def write_value(self, name, value, max_indent = None):
		self.write_types_comment(name)
		if max_indent is None:
			max_indent = self.max_indent

		self.output(name, " = ")
		self.write(value, 1, max_indent)
		self.output("\n\n")

		self.flush()

	def write_comment(self, comment):
		self.output("-- ", comment, "\n")

	def write(self, value, indent = 1, max_indent = 0):
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
			output('"%s"' % format_string(value))

		elif tp == str:
			output('"%s"' % format_string(value.encode("utf-8")))

		elif tp == tuple or tp == list:
			output(self.array_prefix)

			if len(value) == 0:
				output(self.array_posfix)
				return

			for v in value:
				self.newline_indent(indent, max_indent)
				self.write(v, indent + 1, max_indent)
				output(",")

			if indent <= max_indent:
				output("\n")
				self._output(indent - 1, self.array_posfix)
			else:
				output(self.array_posfix)

		elif tp == dict:
			output(self.dict_prefix)
			if len(value) == 0:
				output(self.dict_posfix)
				return

			keys = list(value.keys())
			keys.sort()

			for k in keys:
				self.newline_indent(indent, max_indent)

				output("[")
				self.write(k)
				output("] = ")
				self.write(value[k], indent + 1, max_indent)
				output(",")

			if indent <= max_indent:
				output("\n")
				self._output(indent - 1, self.dict_posfix)
			else:
				output(self.dict_posfix)

		else:
			raise TypeError("unsupported type %s" % str(tp))

		return

	def newline_indent(self, indent, max_indent):
		if indent <= max_indent:
			self.output("\n")
			self._output(indent)
		else:
			self.output(" ")
