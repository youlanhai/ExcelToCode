#-*- coding: utf-8 -*-
import os
import sys
import traceback
from argparse import ArgumentParser

module_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(module_path, "xl2code"))

import util
import xlsconfig
import install_package
from logtool import native_str
from load_configure import load_configure

def main(argv):
	util.redirect_iostream()

	parser = ArgumentParser(description=native_str("导表工具"))
	parser.add_argument("config_file", help=native_str("配置文件路径"))
	parser.add_argument("--gen-header", action="store_true", help=native_str("根据转换器信息生成Excel表头"))
	parser.add_argument("--gen-code", action="store_true", help=native_str("生成代码文件"))
	parser.add_argument("--export", action="store_true", help=native_str("导表"))
	parser.add_argument("--fast-mode", action="store_true", help=native_str("快速导表。Excel没有改动就不进行导表。"))
	parser.add_argument("--force-run", action="store_true", help=native_str("出错后仍然继续下去"))
	parser.add_argument("-input", help=native_str("Excel的输入路径"))
	parser.add_argument("-output", help=native_str("输出路径"))
	parser.add_argument("-temp", help=native_str("临时目录"))
	option = parser.parse_args(argv)

	#parser.print_help()

	try:
		load_configure(option.config_file, option)
	except:
		traceback.print_exc()
		print "Error: Failed to load configure file", option.config_file
		return

	xlsconfig.FAST_MODE = option.fast_mode
	xlsconfig.FORCE_RUN = option.force_run

	if not install_package.check_plugin(("openpyxl", )):
		return

	if option.gen_header:
		import generate_header
		generate_header.generate_header()

	if option.export or option.gen_code:
		if not export_excel():
			return

	if option.gen_code:
		import generate_code
		generate_code.generate_code()

	print "=== 完毕 ===\n"
	return

def export_excel():
	util.safe_makedirs(xlsconfig.TEMP_PATH, not xlsconfig.FAST_MODE)

	try:
		csv_path = os.path.join(xlsconfig.TEMP_PATH, "csv")

		import csvjob
		job = csvjob.CSVJob(
			xlsconfig.INPUT_PATH,
			csv_path,
			xlsconfig.TEMP_PATH,
			xlsconfig.CSV_JOB_COUNT
		)
		job.run()

		import exporters
		cls = getattr(exporters, xlsconfig.EXPORTER_CLASS)
		exporter = cls(csv_path, (".csv", ))
		exporter.run()

	except util.ExcelToCodeException, e:
		split_line = "*" * 70
		print split_line
		print native_str("错误：")
		print e
		print split_line
		exit(-1)
	return True

if __name__ == "__main__":
	main(sys.argv[1:])
