# -*- coding: utf-8 -*-
# 根据表头描述文件，自动生成表头。
# 也可以从表头生成描述文件
#
from os import path
from argparse import ArgumentParser

import util
from util import _S

from excel_parser import ExcelParser

def main():
	parser = ArgumentParser(description = _S("表头生成工具"))
	parser.add_argument("-t", "--excel-to-header", action = "store_true", help = _S("生成表头"))
	parser.add_argument("-f", "--excel-from-header", action = "store_true", help = _S("生成excel表"))
	parser.add_argument("--excel-path", help = _S("excel文件路径"))
	parser.add_argument("--header-path", help = _S("表头文件路径"))

	option = parser.parse_args()

	if option.excel_to_header:
		p = ExcelParser(option.excel_path)
		p.parse()
		p.save(option.header_path)


if __name__ == "__main__":
	main()
