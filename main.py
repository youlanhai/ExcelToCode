#-*- coding: utf-8 -*-
import traceback
import util
import xlsconfig
import install_package
from logtool import native_str
from argparse import ArgumentParser
from load_configure import load_configure

def main():
	parser = ArgumentParser(description=native_str("导表工具"))
	parser.add_argument("config_file", help=native_str("配置文件路径"))
	parser.add_argument("--gen-header", action="store_true", help=native_str("生成Excel表头"))
	parser.add_argument("--gen-code", action="store_true", help=native_str("生成代码文件"))
	parser.add_argument("--export", action="store_true", help=native_str("导表"))
	parser.add_argument("--full-export", action="store_true", help=native_str("完全导表。导表前会清除所有中间数据"))
	parser.add_argument("--encode-log", action="store_true", help=native_str("log编码转换"))
	parser.add_argument("--force-run", action="store_true", help=native_str("出错后仍然继续下去"))
	option = parser.parse_args()

	#parser.print_help()

	try:
		load_configure(option.config_file)
	except:
		traceback.print_exc()
		print "Error: Failed to load configure file", option.config_file
		return

	xlsconfig.FULL_EXPORT = option.full_export
	xlsconfig.FORCE_RUN = option.force_run

	if option.encode_log:
		util.redirect_iostream()

	if not install_package.check_plugin(("openpyxl", )):
		return

	for generator in xlsconfig.DATA_WRITERS:
		util.safe_makedirs(generator["file_path"], xlsconfig.FULL_EXPORT)
		
	for generator in xlsconfig.CODE_GENERATORS:
		util.safe_makedirs(generator["file_path"], xlsconfig.FULL_EXPORT)

	if option.gen_header:
		import generate_header
		generate_header.generate_header()

	if option.export or option.gen_code:
		export_excel()

	if option.gen_code:
		import generate_code
		generate_code.generate_code()

	print "=== 完毕 ===\n"
	return

def export_excel():
	util.safe_makedirs(xlsconfig.TEMP_PATH, xlsconfig.FULL_EXPORT)

	import exporters
	cls = getattr(exporters, xlsconfig.EXPORTER_CLASS)
	exporter = cls(xlsconfig.INPUT_PATH, (".xlsx", ))
	exporter.run()
	return

if __name__ == "__main__":
	main()
