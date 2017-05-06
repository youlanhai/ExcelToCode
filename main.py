#-*- coding: utf-8 -*-
import traceback
import util
import xlsconfig
import install_package
from logtool import native_str
from argparse import ArgumentParser

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
		xlsconfig.load_configure(option.config_file)
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

	import xls2script
	import generate_header
	import generate_code

	if option.gen_header:
		generate_header.generate_header()

	if option.gen_code:
		generate_code.generate_code()

	if option.export or not (option.gen_header or option.gen_code):
		xls2script.export_excel()

if __name__ == "__main__":
	main()
