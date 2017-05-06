# -*- coding: utf-8 -*-
from base_writer import BaseWriter

class PyWriter(BaseWriter):

	def __init__(self, file_path, data_module):
		super(PyWriter, self).__init__(file_path, data_module)
		self.write_comment("-*- coding: utf-8 -*-\n")

	def write_sheet(self, name, sheet):
		output = self.output

		output(name)
		output(" = {\n")

		keys = sheet.keys()
		keys.sort()

		key_format = "\t%d: "
		if len(keys) > 0 and isinstance(keys[0], basestring):
			key_format = "\t\"%s\": "

		for k in keys:
			output(key_format % k)
			self.write(sheet[k])
			output(",\n")

		output("}\n\n")

	def write_value(self, name, value):
		output = self.output

		output(name)
		output(" = ")
		self.write(value)
		output("\n\n")

		self.flush()

	def write_comment(self, comment):
		self.output("# ")
		self.output(comment)
		self.output("\n")

	def write(self, value):
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
			output('"%s"' %(value, ))

		elif tp == unicode:
			output('"%s"' % (value.encode("utf-8"), ))

		elif tp == tuple:
			output("(")
			for v in value:
				self.write(v)
				output(", ")
			output(")")

		elif tp == list:
			output("[")
			for v in value:
				self.write(v)
				output(", ")
			output("]")

		elif tp == set:
			output("set(")
			self.write(sorted(value))
			output(")")

		elif tp == frozenset:
			output("frozenset(")
			self.write(sorted(value))
			output(")")

		elif tp == dict:
			output("{")

			keys = value.keys()
			keys.sort()
			for k in keys:
				self.write(k)
				output(": ")
				self.write(value[k])
				output(", ")

			output("}")

		else:
			raise TypeError, "unsupported type %s" % (str(tp), )

		return
