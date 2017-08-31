# -*- coding: utf-8 -*-
import re
import os
import sys
import traceback
import xlsconfig
import util
from direct_exporter import DirectExporter
from tps import tp0
from parsers.base_parser import ConverterInfo

class MixExporter(DirectExporter):

	def __init__(self, input_path, exts):
		super(MixExporter, self).__init__(input_path, exts)
		self.converter_modules = {}

	def run(self):
		self.gather_excels()

		sys.path.insert(0, xlsconfig.CONVERTER_PATH)
		sys.path.insert(0, xlsconfig.TEMP_PATH)

		# export excels to temp python
		self.export_excels()

		self.write_sheets(xlsconfig.EXPORT_STAGE_BEGIN)

		self.merge_sheets()

		self.post_convert_sheets()

		self.post_process_sheets()

		self.post_check_sheets()

		self.write_sheets(xlsconfig.EXPORT_STAGE_FINAL)

		self.write_configs()

		self.run_postprocessor()

		sys.path.remove(xlsconfig.CONVERTER_PATH)
		sys.path.remove(xlsconfig.TEMP_PATH)

	def find_converter_info(self, infile):
		# 1. 搜索转换表
		for value in xlsconfig.CONVENTION_TABLE:
			pattern = value[0]
			compiled_pattern = re.compile(pattern)

			if compiled_pattern.match(infile):
				converter_name 	= value[1]
				new_name 	= value[2] if len(value) > 2 else None
				sheet_index = value[3] if len(value) > 3 else 0

				outfile = None
				if new_name is None:
					outfile = os.path.splitext(infile)[0]
				else:
					outfile = compiled_pattern.sub(new_name, infile)

				return (converter_name, outfile, sheet_index)

		# 2. 根据相同的目录结构去搜索
		outfile = os.path.splitext(infile)[0]
		converter_file = os.path.join(xlsconfig.CONVERTER_PATH, xlsconfig.CONVERTER_ALIAS, outfile + ".py")
		if os.path.exists(converter_file):
			converter_name = outfile.replace('/', '.').replace('\\', '.')
			return (converter_name, outfile, 0)

		# 3. 使用文件的名称当作转换器
		converter_name = os.path.basename(outfile)
		return (converter_name, outfile, 0)

	def find_converter(self, name):
		converter = self.converter_modules.get(name)
		if converter is None:
			converter = self.load_converter(name)
			self.converter_modules[name] = converter
		return converter

	def load_converter(self, name):
		converter = None
		full_path = os.path.join(xlsconfig.CONVERTER_PATH, xlsconfig.CONVERTER_ALIAS, name.replace('.', '//') + ".py")
		if not os.path.isfile(full_path):
			return None

		full_name = xlsconfig.CONVERTER_ALIAS + "." + name
		converter = util.import_converter(full_name)

		# 此名称有可能是文件夹，要加上校验
		if not hasattr(converter, "CONFIG"):
			return None

		converter._name = name
		return converter

	def post_convert_value(self, converter, value, output_row):
		if converter.convert == tp0.use_empty:
			return

		ret = None
		if value is None or value == "":
			if not converter.is_default:
				raise ValueError, "该项必填"

		else:
			ret = converter.convert(value)

		if ret is None and converter.is_default:
			if not converter.exist_default_value:
				return
			ret = converter.default_value

		output_row[converter.field] = ret

	def post_convert_row(self, field_2_cfg, key_value, row):
		for field, cfg in field_2_cfg.iteritems():
			value = row.pop(field, None)
			try:
				self.post_convert_value(cfg, value, row)
			except:
				traceback.print_exc()
				util.log_error("列(%s, %s)二次转换失败，value = %s", str(key_value), cfg.header, tp0.to_str(value))
		return

	def post_convert_sheet(self, data_module):
		converter = data_module.converter
		if converter is None: return

		print "post convert:", data_module.path

		field_2_cfg = getattr(converter, "FIELD_2_CFG", None)
		if field_2_cfg is None:
			field_2_cfg = {}
			setattr(converter, "FIELD_2_CFG", field_2_cfg)

			for info in converter.CONFIG:
				cfg = ConverterInfo(info)
				field_2_cfg[cfg.field] = cfg

		main_sheet = data_module.main_sheet
		for key, row in main_sheet.iteritems():
			if isinstance(row, list):
				for sub_row in row:
					self.post_convert_row(field_2_cfg, key, sub_row)
			else:
				self.post_convert_row(field_2_cfg, key, row)

	def post_convert_sheets(self):
		print "=== 转换为最终数据 ..."

		for data_module in self.data_modules.itervalues():
			self.post_convert_sheet(data_module)

		return
