# -*- coding: utf-8 -*-
import os
from base_writer import BaseWriter

FORMAT_CHARS = {
	'"'  : '&quot;',
	"'"  : '&apos;',
	'&'  : '&amp;',
	'<'  : '&lt;',
	'>'  : '&gt;',
	' '  : '&nbsp;',
	'©'  : '&copy;',
	'®'  : '&reg;',
	'\t' : '&#x0009;',
	'\r' : '&#x000D;',
	'\n' : '&#x000A;',
}

def format_str(s):
	ret = []
	for ch in s: ret.append(FORMAT_CHARS.get(ch, ch))
	return "".join(ret)


class XMLWriter(BaseWriter):
	def __init__(self, file_path, data_module = None, generator_info = None):
		super(XMLWriter, self).__init__(file_path, data_module, generator_info)
		self.output('<?xml version="1.0" encoding="utf-8"?>\n')
		self.module_name = os.path.splitext(os.path.basename(file_path))[0]

	def write_sheet(self, name, sheet):
		if name != "main_sheet": return

		self.write_types_comment(name)
	
		name = self.module_name
		indent = 0
		self._output_line(indent, '<%s>' % name)

		item_key = name + "Item"

		keys = sheet.keys()
		keys.sort()
		for key in keys:
			self._write_row(item_key, sheet[key], indent + 1)

		self._output_line(indent, "</%s>" % name)

	def _write_row(self, key, value, indent):
		if isinstance(value, list):
			for row in value:
				self.write(key, row, indent)
		else:
			self.write(key, value, indent)

	def _write_list(self, key, value, indent):
		self._output_line(indent, "<%s>" % key)

		for i, v in enumerate(value):
			self.write(key + "Item", v, indent + 1)

		self._output_line(indent, "</%s>" % key)

	def _write_dict(self, key, value, indent):
		self._output_line(indent, "<%s>" % key)

		keys = value.keys()
		keys.sort()

		indent += 1

		for k in keys:
			v = value[k]
			if isinstance(k, str):
				self.write(k, v, indent)
			else:
				self._output_line(indent, "<%sItem>" % key)
				self.write("ID", k, indent + 1)
				self.write("value", v, indent + 1)
				self._output_line(indent, "</%sItem>" % key)

		indent -= 1
		self._output_line(indent, "</%s>" % key)

	def write_value(self, name, value, max_indent = 2):
		pass

	def write_comment(self, comment):
		self.output("<!-- %s -->\n" % comment)

	def to_string(self, value):
		if value is None:
			return ""

		tp = type(value)
		if tp == bool:
			return "true" if value else "false"

		elif tp == int:
			return str(value)

		elif tp == float:
			return "%g" % value

		elif tp == str:
			return format_str(value)

		elif tp == unicode:
			return format_str(value.encode("utf-8"))

		else:
			raise ValueError, "unsupported value type %s" % str(tp)

		return

	def write(self, key, value, indent):
		tp = type(value)
		if tp == tuple or tp == list:
			self._write_list(key, value, indent)

		elif tp == dict:
			self._write_dict(key, value, indent)

		else:
			s = self.to_string(value)
			self._output_line(indent, "<%s>%s</%s>" % (key, s, key))

		return
