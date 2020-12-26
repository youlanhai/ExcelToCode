# -*- coding: utf-8 -*-
"""
将Excel表转换成csv

Excel的解析速度比较慢，可以用多进程转换为csv。
然后再启动导表工具，进行导出处理。

也可以用自定义的Excel-CSV转换工具处理完表格，比如Excel表是分页格式。
然后再启动导表工具，进行导出处理。
"""

from os import path
from argparse import ArgumentParser

from . import util
from .util import _S, log, log_error
from .excel_parser import ExcelParser

def main():
	parser = ArgumentParser(description = _S("将excel表格转换成csv文件"))
	parser.add_argument("-o", "--output", help=_S("输出文件路径。如果输入路径是目录，输出路径也应该是目录"))
	parser.add_argument("-a", "--all-worksheet", action="store_true", help=_S("是否导出所有的sheet页"))
	parser.add_argument("input", help=_S("输入文件路径。可以是文件，也可以是目录"))
	parser.add_argument("-c", "--config-file", help=_S("配置文件。要转换的文件列表，是相对于input的路径"))
	parser.add_argument("-v", "--verbose", action="store_true", help=_S("输出更多日志"))
	parser.add_argument("-i", "--index", default = "", help=_S("当前进程编号"))

	option = parser.parse_args()
	input_path = option.input
	if input_path is None:
		return log_error("没有输入路径")

	output_path = option.output

	if option.config_file:
		if output_path is None:
			output_path = input_path
		parse_config(option.config_file, input_path, output_path, option)
		return

	if path.isfile(input_path):
		if output_path is None:
			output_path = path.splitext(input_path)[0] + ".csv"
		parse_file(input_path, output_path, option)
	else:
		if output_path is None:
			output_path = input_path

		parse_folder(input_path, output_path, option)
	return


def parse_config(config_file, input_path, output_path, option):
	files = []
	with open(config_file, "r") as f:
		for line in f:
			files.append(line.strip())

	parse_files(files, input_path, output_path, option)


def parse_folder(input_path, output_path, option):
	files = util.gather_all_files(input_path, (".xlsx", ))
	parse_files(files, input_path, output_path, option)


def parse_files(files, input_path, output_path, option):
	for fname in files:
		src_path = path.join(input_path, fname)
		dst_path = path.join(output_path, path.splitext(fname)[0] + ".csv")
		parse_file(src_path, dst_path, option)


def parse_file(input_path, output_path, option):
	if option.verbose:
		log("[%s]parse: %s" % (option.index, input_path))

	parser = ExcelParser(
		input_path,
		export_all_sheet = option.all_worksheet
	)
	parser.parse()
	parser.save(output_path)


if __name__ == "__main__":
	main()

	if util.has_error:
		exit(-1)
