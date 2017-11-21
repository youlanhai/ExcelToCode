# -*- coding: utf-8 -*-

import traceback
import xlsconfig
import util
from tps import tp0, convention
from base_parser import ConverterInfo, BaseParser

class ConfigParser(BaseParser):

	def __init__(self, filename, module, sheet_index = 0):
		super(ConfigParser, self).__init__(filename, module, sheet_index)

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

	def parse_header(self, cells):
		super(ConfigParser, self).parse_header(cells)

		for col, header in enumerate(self.headers):
			converter = None

			cfg = self.header_2_config.get(header)
			if cfg is None:
				print "警告：表头%s = '%s'没有被解析。" % (self.row_col_str(self.header_row_index, col), header, )

			else:
				converter = ConverterInfo(cfg)
				field = converter.field

				type = convention.function2type(converter.convert)
				self.sheet_types[field] = (col, field, header, type)

			self.converters[col] = converter

		self.key_name = self.converters[0].field
		return

