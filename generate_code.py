# -*- coding: utf-8 -*-
import os
import sys
import xlsconfig
import util

import codegen

def generate_code():
	print "=== 生成代码类文件 ..."

	for generator in xlsconfig.CODE_GENERATORS:
		util.safe_makedirs(generator["file_path"], xlsconfig.FULL_EXPORT)

	sys.path.insert(0, xlsconfig.CONVERTER_PATH)

	converter_path = os.path.join(xlsconfig.CONVERTER_PATH, xlsconfig.CONVERTER_ALIAS)
	prefix_len = len(converter_path) + 1

	for root, dirs, files in os.walk(converter_path):
		relative_path = root[prefix_len:]

		for fname in files:
			name, ext = os.path.splitext(fname)
			if ext != ".py" or name == "__init__": continue

			module_name = os.path.join(relative_path, name)
			module = util.import_file(xlsconfig.CONVERTER_ALIAS + "." + module_name)
			if getattr(module, "CONFIG", None) is None: continue

			_generate(module, module_name)

	sys.path.remove(xlsconfig.CONVERTER_PATH)

def _generate(module, module_name):
	for generator in xlsconfig.CODE_GENERATORS:
		cls = getattr(codegen, generator["class"])
		output_path = generator["file_path"]

		gen = cls(module, module_name, output_path)
		gen.run()
