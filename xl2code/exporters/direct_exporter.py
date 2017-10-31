# -*- coding: utf-8 -*-
import os
import traceback
import time

import xlsconfig
import util

from parsers import DirectParser
from base_exporter import BaseExporter

STAGES_INFO = [
	{"class" : "MergeSheets", },
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_RAW},
	{"class" : "MergeField"},
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_BEGIN},
	{"class" : "MergeFiles"},
	{"class" : "WriteSheets", "stage" : xlsconfig.EXPORT_STAGE_FINAL},
	{"class" : "WriteConfigure"},
	{"class" : "WriteFileList"},
	{"class" : "RunCustomStage"},
]

def resolve_path(infile, path):
	if path.startswith('/'):
		path = path[1:]
	else:
		path = os.path.normpath(os.path.join(os.path.dirname(infile), path))
	return path


class DirectExporter(BaseExporter):
	STAGES_INFO = STAGES_INFO

	def __init__(self, input_path, exts):
		super(DirectExporter, self).__init__(input_path, exts)
		self.parser_class = DirectParser
		self.merge_file_patterns = []

	def export_excels(self):
		for infile in self.excel_files:
			if self.parse_excel(infile, 0):
				pass

			elif not xlsconfig.FORCE_RUN:
				return
		return

	def parse_excel(self, infile, sheet_index = 0):
		input_full_path = os.path.join(xlsconfig.INPUT_PATH, infile)
		data_module = None
		outfile = None

		if xlsconfig.FAST_MODE:
			info = self.parser_cache.get(infile)
			if info and info["createTime"] >= os.path.getmtime(input_full_path):
				outfile = info["outputPath"]
				data_module = util.import_file(outfile)

		if data_module is None:
			print "parse", infile

			parser = self.parser_class(input_full_path, None, sheet_index)
			try:
				parser.run()
			except:
				traceback.print_exc()
				return False

			arguments = parser.arguments

			outfile = arguments.get("outputPath")
			if outfile is None:
				outfile = os.path.splitext(infile)[0]
			else:
				outfile = resolve_path(infile, outfile)

			outfile = outfile.replace('\\', '/')

			converter_name = arguments.get("template")
			if converter_name is None:
				converter_name = self.match_converter(outfile)
			converter_name = converter_name.replace('\\', '/').replace('/', '.')

			data_module = self.create_data_module(infile, outfile, converter_name, parser)
			if data_module is None:
				return False

			self.parser_cache[infile] = {
				"outputPath" : outfile,
				"createTime" : time.time(),
			}

		arguments = data_module.info["arguments"]

		merge_to_sheet = arguments.get("mergeToSheet")
		if merge_to_sheet:
			to_name = resolve_path(infile, merge_to_sheet)
			self.add_merge_sheet_pattern(to_name, outfile)

		merge_to_file = arguments.get("mergeToFile")
		if merge_to_file:
			to_name = resolve_path(infile, merge_to_file)
			self.add_merge_file_pattern(to_name, outfile)

		self.store_data_module(data_module)
		return True

	def match_converter(self, outfile):
		return outfile

	def add_merge_pattern(self, pattern_list, to_name, sub_name):
		# 如果目标表格存在，则追加到尾部
		for i, pattern in enumerate(pattern_list):
			if to_name != pattern[0]: continue

			for j in xrange(1, len(pattern)):
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





