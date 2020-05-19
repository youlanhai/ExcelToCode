# -*- coding: utf-8 -*-
# 根据表头描述文件，自动生成表头。
# 也可以从表头生成描述文件
#
from os import path
from argparse import ArgumentParser

import util
from util import _S, ExcelToCodeException

try:
	import openpyxl
except:
	raise ExcelToCodeException("请安装插件: openpyxl")

from excel_parser import ExcelParser

def main():
	parser = ArgumentParser(description = _S("表头生成工具"))
	parser.add_argument("-t", "--excel-to-header", action = "store_true", help = _S("生成表头描述文件"))
	parser.add_argument("-f", "--excel-from-header", action = "store_true", help = _S("根据表头描述文件生成excel表"))
	parser.add_argument("--excel-path", help = _S("excel文件路径"))
	parser.add_argument("--header-path", help = _S("表头文件路径"))
	parser.add_argument("--force", action = "store_true", help = _S("强制生成表头"))

	option = parser.parse_args()

	if option.excel_to_header:
		excel_to_header(option.excel_path, option.header_path, path.isdir(option.excel_path))
	elif option.excel_from_header:
		excel_from_header(option.excel_path, option.header_path, path.isdir(option.header_path), option.force)

	if util.has_error:
		exit(-1)

def excel_to_header(excel_path, header_path, recursive):
	if not recursive:
		try:
			p = ExcelParser(excel_path)
			p.parse()
			p.save(header_path)
		except ExcelToCodeException as e:
			util.log_error(str(e))
		return

	files = util.gather_all_files(excel_path, (".xlsx", ))
	util.log("发现excel文件数量: %d", len(files))

	for file_path in files:
		excel_full_path = path.join(excel_path, file_path)
		header_full_path = path.join(header_path, path.splitext(file_path)[0] + ".txt")

		excel_to_header(excel_full_path, header_full_path, False)


def excel_from_header(excel_path, header_path, recursive, force = False):
	if not recursive:
		try:
			p = ExcelParser(excel_path, force = force, auto_create = True)
			p.parse()
			p.generate_header(header_path)
		except ExcelToCodeException as e:
			util.log_error(str(e))
		return

	files = util.gather_all_files(header_path, (".txt", ))
	util.log("发现表头文件数量: %d", len(files))

	for file_path in files:
		excel_full_path = path.join(excel_path, path.splitext(file_path)[0] + ".xlsx")
		header_full_path = path.join(header_path, file_path)

		excel_from_header(excel_full_path, header_full_path, False, force = force)


if __name__ == "__main__":
	main()
