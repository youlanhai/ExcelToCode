# -*- coding: utf-8 -*-
from base_writer import BaseWriter

class LuaWriter(BaseWriter):

	def begin_write(self):
		super(LuaWriter, self).begin_write()
		self.output("module(...)", "\n\n")

	def write_sheet(self, name, sheet):
		self.write_value(name, sheet)

		if name == "main_sheet":
			self.write_value("main_length", len(sheet), 0)

			keys = sheet.keys()
			keys.sort()
			self.write_value("main_keys", keys, 0)

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
			output('"%s"' %(value, ))

		elif tp == unicode:
			output('"%s"' % (value.encode("utf-8"), ))

		elif tp == tuple or tp == list:
			output("{")

			for v in value:
				self.newline_indent(indent, max_indent)
				self.write(v, indent + 1, max_indent)
				output(", ")

			if len(value) > 0 and indent <= max_indent:
				output("\n")
				self._output(indent - 1, "}")
			else:
				output("}")

		elif tp == dict:
			output("{")
			keys = value.keys()
			keys.sort()

			for k in keys:
				self.newline_indent(indent, max_indent)

				output("[")
				self.write(k)
				output("] = ")
				self.write(value[k], indent + 1, max_indent)
				output(", ")

			if len(value) > 0 and indent <= max_indent:
				output("\n")
				self._output(indent - 1, "}")
			else:
				output("}")

		else:
			raise TypeError, "unsupported type %s" % (str(tp), )

		return

	def newline_indent(self, indent, max_indent):
		if indent <= max_indent:
			self.output("\n")
			self._output(indent)
