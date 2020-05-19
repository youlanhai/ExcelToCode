# -*- coding: utf-8 -*-
import sys
import os
from os import path
import numfmt

sys_encoding = (sys.stdout.encoding or "utf-8").lower()

has_error = False

class ExcelToCodeException(Exception):
	pass

def _S(s):
	if sys_encoding != "utf-8":
		if isinstance(s, unicode):
			return s.encode(sys_encoding)
		s = str(s)
		try:
			return s.decode("utf-8").encode(sys_encoding)
		except UnicodeDecodeError:
			pass
	return s

# 打印错误日志。如果不是FORCE_FUN模式，会将错误日志以异常的形式抛出。
def log_error(msg, *args):
	if len(args) > 0:
		msg = msg % args

	global has_error
	has_error = True
	print _S("错误："), _S(msg)

def log(*args):
	ret = []
	if sys_encoding == "utf-8":
		for v in args:
			if isinstance(v, unicode):
				v = v.encode('utf-8')
			else:
				v = str(v)
			ret.append(v)
	else:
		for v in args:
			if not isinstance(v, unicode):
				v = str(v).decode('utf-8')
			ret.append(v)

	try:
		msg = " ".join(ret)
		print msg
	except:
		print ret


def int_to_base26(value):
	asciiA = ord('A')

	value += 1

	ret = ""
	while value != 0:
		mod = value % 26
		value = value // 26
		if mod == 0:
			mod = 26
			value -= 1

		ret = chr(asciiA + mod - 1) + ret

	return ret

# 确保文件所在的路径存在。file_path是文件的路径。
def ensure_folder_exist(file_path):
	output_dir = path.dirname(file_path)
	if not path.isdir(output_dir):
		try:
			os.makedirs(output_dir)
		except Exception, e:
			print e

	return

# 收集path目录下所有后缀符合exts的文件。
# 返回的路径是相对于path的相对路径。
def gather_all_files(path, exts):
	ret = []
	path = path.decode("utf-8")

	path_len = len(path)
	if path[-1] != '/':
		path_len += 1

	for root, dirs, files in os.walk(path):
		i = 0
		while i < len(dirs):
			if dirs[i][0] == '.':
				dirs.pop(i)
			else:
				i += 1

		relative_path = root[path_len:]

		for fname in files:
			if fname.startswith("~$"):
				continue

			ext = os.path.splitext(fname)[1]
			if ext not in exts:
				continue

			file_path = os.path.join(relative_path, fname)
			ret.append(file_path.encode("utf-8").replace('\\', '/'))

	return ret

# 因为'123,456'格式的字符串，会被Excel存贮成浮点数：123456，
# 而openpyxl仅仅是读取存贮的数据，不会自动将数字还原成字符串，所以这里手动进行转换。
def format_number(f, cell, parser):
	a_fmt = numfmt.extract_number_format(cell.number_format)
	if a_fmt:
		return numfmt.format_number(f, a_fmt, ',', '.')
	else:
		s = "%f" % f
		# 删除'.'后面的0
		return remove_end_zero(s)

def remove_end_zero(s):
	pos = s.find('.')
	if pos < 0:
		return s

	i = len(s)
	while i > pos and s[i - 1] == '0':
		i -= 1
	if s[i - 1] == '.':
		i -= 1
	return s[:i]
