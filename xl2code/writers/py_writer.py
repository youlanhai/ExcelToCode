# -*- coding: utf-8 -*-
from .base_writer import BaseWriter
from util import format_string

class PyWriter(BaseWriter):

	def __init__(self, file_path, data_module = None, generator_info = None):
		super(PyWriter, self).__init__(file_path, data_module, generator_info)
		self.write_comment("-*- coding: utf-8 -*-\n")

	def write_sheet(self, name, sheet):
		self.write_value(name, sheet)

	def write_value(self, name, value):
		self.write_types_comment(name)
		self.output("\n")

		self.output(name, " = ")
		self.write(value, 1, self.max_indent)
		self.output("\n\n")

		self.flush()

	def write_comment(self, comment):
		self.output("# ", comment, "\n")

	def write(self, value, indent = 1, max_indent = 0):
		output = self.output

		if value is None:
			return output("None")

		tp = type(value)
		if tp == bool:
			output("True" if value else "False")

		elif tp == int:
			output("%d" % (value, ))

		elif tp == float:
			output("%g" % (value, ))

		elif tp == str:
			output('"%s"' % format_string(value))

		elif tp == tuple:
			self._write_list(value, "(", ")", indent, max_indent)

		elif tp == list:
			self._write_list(value, "[", "]", indent, max_indent)

		elif tp == set:
			self._write_list(sorted(value), "set(", ")", indent, max_indent)

		elif tp == frozenset:
			self._write_list(sorted(value), "frozenset(", ")", indent, max_indent)

		elif tp == dict:
			output("{")

			keys = list(value.keys())
			keys.sort()

			for k in keys:
				self.newline_indent(indent, max_indent)
				self.write(k)
				output(": ")
				self.write(value[k], indent + 1, max_indent)
				output(", ")

			self.endlist_indent(value, "}", indent, max_indent)

		else:
			raise TypeError("unsupported type %s" % str(tp))

		return

	def _write_list(self, value, prefix, posfix, indent, max_indent):
		self.output(prefix)

		for v in value:
			self.newline_indent(indent, max_indent)
			self.write(v, indent + 1, max_indent)
			self.output(", ")

		self.endlist_indent(value, posfix, indent, max_indent)

	def newline_indent(self, indent, max_indent):
		if indent <= max_indent:
			self.output("\n")
			self._output(indent)
		return

	def endlist_indent(self, value, posfix, indent, max_indent):
		if len(value) > 0 and indent <= max_indent:
			self.output("\n")
			self._output(indent - 1, posfix)
		else:
			self.output(posfix)
		return
