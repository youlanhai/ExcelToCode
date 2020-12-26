# -*- coding: utf-8 -*-
import os

import xlsconfig
import util

from parsers import DirectParser
from .base_exporter import BaseExporter

STAGES_INFO = [
	{"class" : "ParseExcel"},
	{"class" : "MergeSheets", },
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_RAW},
	{"class" : "ExtractLocale"},
	{"class" : "MergeField"},
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_BEGIN},
	{"class" : "ExtractConstant"},
	{"class" : "MergeFiles"},
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_FINAL},
	{"class" : "WriteConfigure"},
	{"class" : "WriteFileList"},
	{"class" : "RunCustomStage"},
]

def resolve_output_path(infile, path):
	if path is None:
		path = os.path.splitext(infile)[0]
	elif path.startswith('/'):
		path = path[1:]
	else:
		dir = os.path.dirname(infile)
		path = os.path.normpath(os.path.join(dir, path))
	path = path.replace('\\', '/')

	if xlsconfig.OUTPUT_PATH_TO_LOWER:
		path = path.lower()
	return path


class DirectExporter(BaseExporter):
	STAGES_INFO = STAGES_INFO

	def __init__(self, input_path, exts):
		super(DirectExporter, self).__init__(input_path, exts)
		self.parser_class = DirectParser

	def export_excels(self):
		for infile in self.excel_files:
			error = None
			try:
				ok = self.parse_excel(infile, 0)
				if not ok:
					error = "导表失败"
			except Exception as e:
				error = e
				import traceback
				traceback.print_exc()

			if error:
				util.log_error(error, file = infile)
		return

	def parse_excel(self, infile, sheet_index = 0):
		input_full_path = os.path.join(self.input_path, infile)

		data_module = self._parse(infile, input_full_path, sheet_index)
		if data_module is None:
			return False

		info = data_module.info
		outfile = info["outfile"]

		merge_to_sheet = info.get("mergeToSheet")
		if merge_to_sheet:
			self.add_merge_sheet_pattern(merge_to_sheet, outfile)

		merge_to_file = info.get("mergeToFile")
		if merge_to_file:
			self.add_merge_file_pattern(merge_to_file, outfile)

		self.store_data_module(data_module)
		return True

	def _parse(self, infile, input_full_path, sheet_index):
		# util.log("parse", infile)

		parser = self.parser_class(input_full_path, None, sheet_index)
		parser.run()

		info = {}
		arguments = parser.arguments

		outfile = resolve_output_path(infile, arguments.get("outputPath"))

		converter_name = arguments.get("template")
		if converter_name is None:
			converter_name = self.match_converter(outfile)
		converter_name = converter_name.replace('\\', '/').replace('/', '.')

		merge_to_sheet = arguments.get("mergeToSheet")
		if merge_to_sheet:
			info["mergeToSheet"] = resolve_output_path(infile, merge_to_sheet)

		merge_to_file = arguments.get("mergeToFile")
		if merge_to_file:
			info["mergeToFile"] = resolve_output_path(infile, merge_to_file)

		data_module = self.create_data_module(infile, outfile, converter_name, parser, info)
		if data_module is None:
			return None

		return data_module

	def match_converter(self, outfile):
		return outfile

	def add_merge_pattern(self, pattern_list, to_name, sub_name):
		sub_name = '^' + sub_name + '$'
		# 如果目标表格存在，则追加到尾部
		for i, pattern in enumerate(pattern_list):
			if to_name != pattern[0]:
				continue

			for j in range(1, len(pattern)):
				if sub_name == pattern[j]:
					return

			if not isinstance(pattern, list):
				pattern = list(pattern)
				pattern_list[i] = pattern

			pattern.append(sub_name)
			return

		pattern_list.append([to_name, sub_name])

	def add_merge_sheet_pattern(self, to_name, sub_name):
		self.add_merge_pattern(self.merge_patterns, to_name, sub_name)

	def add_merge_file_pattern(self, to_name, sub_name):
		self.add_merge_pattern(self.merge_file_patterns, to_name, sub_name)
