# -*- coding: utf-8 -*-
import os
import sys
import shutil
import xlsconfig
import util

from codegen.java_code_gen import JavaCodeGen

def generate_code():
	output_path = xlsconfig.JAVA_CODE_PATH
	util.safe_makedirs(output_path, xlsconfig.FULL_EXPORT)

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

			gen = JavaCodeGen(module, module_name, output_path)
			gen.run()

	sys.path.remove(xlsconfig.CONVERTER_PATH)

if __name__ == "__main__":
	generate_code()
