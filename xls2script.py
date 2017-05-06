# -*- coding: utf-8 -*-

import os
import sys
import shutil
import re
import traceback

import xlsconfig
import xlsparser
import writers
import util
from tps import tp0


def export_excel_to_python(infile, outfile, converter, sheet_index = 0):
	input_path = os.path.join(xlsconfig.INPUT_PATH, infile)
	output_path = os.path.join(xlsconfig.TEMP_PATH, outfile + ".py")

	converter_file = os.path.splitext(converter.__file__)[0] + ".py"
	
	if not xlsconfig.FULL_EXPORT and util.if_file_newer(output_path, input_path) and util.if_file_newer(output_path, converter_file):
		return True

	print infile, "-", converter._name
	util.ensure_package_exist(xlsconfig.TEMP_PATH, outfile)

	parser = xlsparser.createParser(input_path, converter, sheet_index)
	try:
		pre_process = getattr(converter, "pre_process", None)
		if pre_process: pre_process(parser)

		parser.do_parse()
	except:
		traceback.print_exc()
		return False

	info = {
		"infile" : infile,
		"outfile" : outfile,
		"parser" : converter._name,
		"sheet_types" : parser.sheet_types,
		"key_name" : getattr(converter, "KEY_NAME", "ID"),
		"need_post_process" : getattr(converter, "post_process", None) != None,
		"need_post_check" :  getattr(converter, "post_check", None) != None,
	}

	wt = writers.PyWriter(output_path, None)
	wt.begin_write()

	wt.write_sheet("info", info)
	wt.write_sheet("main_sheet", parser.sheet)

	wt.end_write()
	wt.close()

	return True

def post_convert_sheet(data_module):
	info = data_module.info
	converter_name = info["parser"]
	converter = util.import_file(converter_name)

	field_2_cfg = {}
	for cfg in converter.CONFIG:
		field = cfg[1]
		field_2_cfg[field] = cfg

	main_sheet = data_module.main_sheet
	for key, row in main_sheet.iteritems():
		if isinstance(row, list):
			for sub_row in row:
				post_convert_row(field_2_cfg, key, sub_row)
		else:
			post_convert_row(field_2_cfg, key, row)

	post_process = getattr(converter, "post_process", None)
	if post_process:
		try:
			data_module.extra_sheets = post_process(main_sheet)
		except:
			traceback.print_exc()
			util.log_error("后处理执行失败 '%s'", info["infile"])

	return True

def post_convert_row(field_2_cfg, key, row):
	keys = row.keys()
	for k in keys:
		cfg = field_2_cfg[k]
		method = cfg[2]
		if method == tp0.use_empty:
			row.pop(k)
			continue

		try:
			row[k] = method(row[k])
		except:
			traceback.print_exc()
			util.log_error("列(%s, %s)二次转换失败，value = %s", str(key), cfg[0], str(row[k]))
	return

def convert_python_to_other(infile):
	data_module = util.import_file(infile)
	info = data_module.info

	outfile = info["outfile"]
	fpath, fname = os.path.split(outfile)
	outfile = os.path.join(fpath, "d_" + fname)

	# 写出裸数据
	_output_to_files(xlsconfig.EXPORT_STAGE_BEGIN, outfile, data_module)
	
	# 执行二次转换
	post_convert_sheet(data_module)

	_output_to_files(xlsconfig.EXPORT_STAGE_FINAL, outfile, data_module)
	return True

def _output_to_files(stage, name, data_module):
	for info in xlsconfig.DATA_WRITERS:
		if info["stage"] != stage: continue
		full_path = os.path.join(info["file_path"], name + info["file_posfix"])

		_output_to_file(info["class"], full_path, data_module)

def _output_to_file(writer_name, output_file, data_module):
	util.ensure_folder_exist(output_file)

	writer_class = getattr(writers, writer_name)
	wt = writer_class(output_file, data_module)
	wt.write_comment("此文件由导表工具自动生成，禁止手动修改。")
	wt.write_comment("from " + data_module.info["infile"])
	wt.output("\n")

	wt.begin_write()
	wt.write_sheet("main_sheet", data_module.main_sheet)

	extra_sheets = getattr(data_module, "extra_sheets", None)
	if extra_sheets is not None:
		assert(isinstance(extra_sheets, dict))
		wt.write_module(extra_sheets)

	wt.end_write()
	wt.close()
	return

def export_excels(excel_files, output_files):
	print "=== 转换为中间文件 ..."

	file_2_converter = {}

	for value in xlsconfig.CONVENTION_TABLE:
		pattern 	= value[0]
		converter_name 	= xlsconfig.CONVERTER_ALIAS + "." + value[1]
		new_name 	= value[2] if len(value) > 2 else None
		sheet_index = value[3] if len(value) > 3 else 0

		compiled_pattern = re.compile(pattern)

		converter = util.import_file(converter_name)
		converter._name = converter_name

		for infile in excel_files:
			if not compiled_pattern.match(infile): continue
			if infile in file_2_converter:
				util.log_error("文件'%s'匹配到了多个转换器", infile)

			file_2_converter[infile] = util.to_class_name(value[1].split('.')[-1])

			outfile = None
			if new_name is None:
				outfile = os.path.splitext(infile)[0]
			else:
				outfile = compiled_pattern.sub(new_name, infile)

			if export_excel_to_python(infile, outfile, converter, sheet_index):
				output_files.append(outfile)

			elif not xlsconfig.FORCE_RUN:
				return

	for info in xlsconfig.DATA_WRITERS:
		if info["stage"] != xlsconfig.EXPORT_STAGE_LIST: continue
		full_path = os.path.join(info["file_path"], info["file_posfix"])

		write_file_list(info["class"], full_path, file_2_converter)

	return

def write_file_list(writer_name, full_path, file_2_converter):
	util.ensure_folder_exist(full_path)

	cls = getattr(writers, writer_name)
	wt = cls(full_path, None)
	wt.begin_write()
	wt.write_sheet("files", file_2_converter)
	wt.end_write()
	wt.close()
	return

def merge_sheets(sheet_files):
	print "=== 合并分表 ..."

	for value in xlsconfig.MERGE_TABLE:
		outfile = value[0]

		sub_files = []

		for i in xrange(1, len(value)):
			compiled_pattern = re.compile(value[i])

			for infile in sheet_files:
				if compiled_pattern.match(infile):
					sub_files.append(infile)

		if len(sub_files) > 0:
			merge_sub_files(outfile, sub_files)

			for sub_file in sub_files:
				sheet_files.remove(sub_file)

			sheet_files.append(outfile)

	return

def merge_sub_files(outfile, sub_files):
	assert(len(sub_files) > 0)
	print "合并", outfile, "<-", sub_files

	util.ensure_package_exist(xlsconfig.TEMP_PATH, outfile)
	new_path = os.path.join(xlsconfig.TEMP_PATH, outfile + ".py")

	info = None
	infiles = []
	sheet = {}

	for sub_file in sub_files:
		module = util.import_file(sub_file)

		info = module.info
		sheet.update(module.main_sheet)

		infiles.append(info["infile"])

		#os.remove(os.path.join(TEMP_PATH, sub_file + ".py"))

	info["infile"] = ", ".join(infiles)
	info["outfile"] = outfile

	wt = writers.PyWriter(new_path, None)
	wt.begin_write()
	wt.output("\n")
	wt.write_sheet("info", info)
	wt.write_sheet("main_sheet", sheet)
	wt.end_write()
	wt.close()

	return

def convert_sheets(sheet_files):
	print "=== 转换为最终数据 ..."

	for path in sheet_files:
		convert_python_to_other(path)

	return

def check_sheet(infile):

	data_module = util.import_file(infile)
	info = data_module.info

	if not info["need_post_check"]:
		return

	print "检查", infile
	converter = util.import_file(info["parser"])

	try:
		converter.post_check(data_module)
	except:
		traceback.print_exc()
		print "错误：文件‘%s’检查失败" % infile

	return

def post_check_sheets(sheet_files):
	print "=== 数据合法性检查 ..."

	for path in sheet_files:
		check_sheet(path)

	return

def export_in_path(path):
	print "=== 搜索Excel文件 ..."
	
	excel_files = util.gather_all_files(path, set((".xlsx", )))
	print "发现 %d 个excel文件" % len(excel_files)

	sheet_files = []
	sys.path.insert(0, xlsconfig.CONVERTER_PATH)

	# export excels to temp python
	export_excels(excel_files, sheet_files)

	sys.path.insert(0, xlsconfig.TEMP_PATH)

	# merge sub sheet
	merge_sheets(sheet_files)

	# convert temp python to script
	convert_sheets(sheet_files)

	post_check_sheets(sheet_files)

	sys.path.remove(xlsconfig.CONVERTER_PATH)
	sys.path.remove(xlsconfig.TEMP_PATH)
	return

def export_excel():
	util.safe_makedirs(xlsconfig.TEMP_PATH, xlsconfig.FULL_EXPORT)

	for info in xlsconfig.DATA_WRITERS:
		path = info["file_path"]
		util.safe_makedirs(path, xlsconfig.FULL_EXPORT)

	export_in_path(xlsconfig.INPUT_PATH)

	print "=== 完毕 ===\n"
	return
