# -*- coding: utf-8 -*-
import traceback
from tps import tp0
import util
from BaseStage import BaseStage
from parsers.base_parser import ConverterInfo

class ConvertField(BaseStage):

	def get_desc(self): return "二次转换数据"

	def process_sheet(self, data_module):
		converter = data_module.converter
		if converter is None: return

		print "post convert:", data_module.path

		col_2_cfg = getattr(converter, "COL_2_CFG", None)
		if col_2_cfg is None:
			col_2_cfg = {}
			setattr(converter, "COL_2_CFG", col_2_cfg)

			types = data_module.info["sheet_types"]["main_sheet"]
			for info in converter.CONFIG:
				header = info[0]
				type_info = types.get(header)
				if type_info is None:
					print "header '%s' doesn't exist" % header
					continue

				col = type_info[0]

				cfg = ConverterInfo(info, col)
				col_2_cfg[col] = cfg

		multiKey = data_module.info["arguments"].get("multiKey")
		main_sheet = data_module.main_sheet
		for key, row in main_sheet.iteritems():
			if multiKey:
				for sub_row in row:
					self.post_convert_row(col_2_cfg, key, sub_row)
			else:
				self.post_convert_row(col_2_cfg, key, row)

		return

	def post_convert_value(self, converter, value):
		if converter.convert == tp0.use_empty:
			return None

		ret = None
		if value is None or value == "":
			if not converter.can_default:
				raise ValueError, "该项必填"

		else:
			ret = converter.convert(value)

		if ret is None and converter.exist_default_value:
			ret = converter.default_value

		return ret

	def post_convert_row(self, col_2_cfg, key_value, row):
		for col, cfg in col_2_cfg.iteritems():
			value = row[col]
			try:
				row[col] = self.post_convert_value(cfg, value)
			except:
				traceback.print_exc()
				util.log_error("key: %s, 列: %s, 二次转换失败，value = %s", str(key_value), util.int_to_base26(col), tp0.to_str(value))
		return

