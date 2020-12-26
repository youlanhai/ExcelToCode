# -*- coding: utf-8 -*-
import sys
import os
from os import path

sys_encoding = (sys.stdout.encoding or "utf-8").lower()

has_error = False

class ExcelToCodeException(Exception):
	def __init__(self, value = "", file = ""):
		if isinstance(value, ExcelToCodeException):
			self.value = value.value
			self.file = value.file
		else:
			self.value = value
			self.file = str(file)

	def __str__(self):
		return "%s, file: %s" % (self.value, self.file)

def _S(s):
	if sys_encoding != "utf-8":
		if isinstance(s, str):
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
	print(_S("错误："), _S(msg))

def log(msg, *args):
	if len(args) > 0:
		msg = msg % args

	print(_S(msg))


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

def row_col_str(row, col):
	return "%s:%d" % (int_to_base26(col), row + 1)

# 确保文件所在的路径存在。file_path是文件的路径。
def ensure_folder_exist(file_path):
	output_dir = path.dirname(file_path)
	if not path.isdir(output_dir):
		try:
			os.makedirs(output_dir)
		except Exception as e:
			print(e)

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

def byteify(input):
	if isinstance(input, dict):
		return {byteify(key): byteify(value) for key, value in input.items()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, str):
		return input.encode('utf-8')
	else:
		return input
