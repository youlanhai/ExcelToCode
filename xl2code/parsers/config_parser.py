# -*- coding: utf-8 -*-

import traceback
import xlsconfig
import util
from tps import tp0, convention
from base_parser import ConverterInfo, BaseParser

class ConfigParser(BaseParser):

	def __init__(self, filename, module, sheet_index = 0):
		super(ConfigParser, self).__init__(filename, module, sheet_index)

		self.key_name = getattr(module, "KEY_NAME", "ID")
		self.is_multi_key = getattr(module, "MULTI_KEY", False)

		self.config = getattr(module, "CONFIG", None)
		
		self.header_2_config = {}

	def run(self):
		self.map_config_array_to_dict()
		self.do_parse()

	def map_config_array_to_dict(self):
		ret = {}
		for info in self.config:
			header = info[0]
			ret[header] = info
		self.header_2_config = ret

	def parse_header(self, rows):
		super(ConfigParser, self).parse_header(rows)

		for col, header in enumerate(self.headers):
			converter = None

			cfg = self.header_2_config.get(header)
			if cfg is None:
				print "警告：第(%s)列的表头'%s'没有被解析。%s" % (util.int_to_base26(col), header, self.filename, )

			else:
				converter = ConverterInfo(cfg)
				field = converter.field

				type = convention.function2type(converter.convert)
				self.sheet_types[field] = (col, field, header, type)

			self.converters[col] = converter

		return

