#-*- coding: utf-8 -*-
import os
import sys
import traceback
from argparse import ArgumentParser

module_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(module_path, "xl2code"))

import util
import xlsconfig
from misc import install_package
from util import _S, ExcelToCodeException
from load_configure import load_configure

def main(argv):
	# util.redirect_iostream()

	parser = ArgumentParser(description=_S("导表工具"))
	parser.add_argument("config_file", help=_S("配置文件路径"))
	parser.add_argument("--gen-header", action="store_true", help=_S("根据转换器信息生成Excel表头"))
	parser.add_argument("--gen-code", action="store_true", help=_S("生成代码文件"))
	parser.add_argument("--export", action="store_true", help=_S("导表"))
	parser.add_argument("--fast-mode", action="store_true", help=_S("快速导表。Excel没有改动就不进行导表。"))
	parser.add_argument("--force-run", action="store_true", help=_S("出错后仍然继续下去"))
	parser.add_argument("-input", help=_S("Excel的输入路径"))
	parser.add_argument("-output", help=_S("输出路径"))
	parser.add_argument("-temp", help=_S("临时目录"))
	option = parser.parse_args(argv)

	#parser.print_help()

	try:
		load_configure(option.config_file, option)
	except ExcelToCodeException, e:
		util.log(e)
		exit(-1)
	except:
		traceback.print_exc()
		util.log("Error: Failed to load configure file", option.config_file)
		exit(-1)

	xlsconfig.FAST_MODE = option.fast_mode
	xlsconfig.FORCE_RUN = option.force_run

	if not install_package.check_plugin(("openpyxl", )):
		exit(-1)

	if option.gen_header:
		from misc import generate_header
		generate_header.generate_header()

	if option.export or option.gen_code:
		if not export_excel():
			exit(-1)

	if option.gen_code:
		from misc import generate_code
		generate_code.generate_code()

	util.log("=== 完毕 ===\n")
	return

def export_excel():
	util.safe_makedirs(xlsconfig.TEMP_PATH, not xlsconfig.FAST_MODE)

	try:
		csv_path = os.path.join(xlsconfig.TEMP_PATH, "csv")
		util.log("=== excel to csv ===")

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

	except ExcelToCodeException, e:
		split_line = "*" * 70
		util.log(split_line)
		util.log("错误：")
		util.log(e)
		util.log(split_line)
		exit(-1)
	return True

if __name__ == "__main__":
	main(sys.argv[1:])
