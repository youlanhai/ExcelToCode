# -*- coding: utf-8 -*-
import os
import sys
import shutil
import re
import time
import locale

import xlsconfig

sys_encoding = (sys.stdout.encoding or "utf-8").lower()
print "sys encoding:", sys_encoding

has_error = False

SPLIT_LINE = "*" * 70

class ExcelToCodeException(Exception):
	def __init__(self, value = "", file = ""):
		if isinstance(value, ExcelToCodeException):
			self.value = value.value
		else:
			self.value = str(value)
		self.file = str(file)

	def __str__(self):
		return "%s, file: %s" % (self.value, self.file)

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

def to_utf8(s):
	tp = type(s)
	if tp == unicode: return s.encode("utf-8")
	if tp == str: return s
	return s

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

def base26_to_int(value):
	asciiA = ord('A')

	ret = 0
	for s in value:
		ret = ret * 26 + ord(s) - asciiA + 1

	return ret - 1


# 转换成类的名称格式。首字母大写驼峰法。
def to_class_name(name):
	strs = name.split('_')
	for i, s in enumerate(strs):
		if len(s) > 0:
			s = s[0].upper() + s[1:]
		strs[i] = s
	return "".join(strs)

# 根据python文件路径进行import。
# filename 可以是路径，也可以是'.'分割的串，但不能有后缀名。
def import_file(filename):
	module_name = filename.replace("/", '.')
	only_name = module_name.split('.')[-1]
	return __import__(module_name, globals(), locals(), [only_name, ])

# 导入转换器配置模块
def import_converter(filename):
	module = import_file(filename)
	cfg = getattr(module, "CONFIG")

	# 旧版CONFIG是dict格式的，这里要做一个兼容
	if isinstance(cfg, dict):
		new_cfg = []
		for k, v in cfg.iteritems():
			new_v = list(v)
			new_v.insert(0, k)
			new_cfg.append(new_v)
		module.CONFIG = new_cfg
	return module


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
				v = str(v)
				try:
					v = v.decode('utf-8')
				except:
					try:
						v = v.decode(sys_encoding)
					except:
						pass
			ret.append(v)

	try:
		msg = " ".join(ret)
		print msg
	except:
		print ret

def log_verbose(*args):
	pass

# 打印错误日志。如果不是FORCE_FUN模式，会将错误日志以异常的形式抛出。
def log_error(msg, *args, **kargs):
	if len(args) > 0: msg = msg % args

	file = kargs and kargs.get("file")

	if xlsconfig.FORCE_RUN:
		global has_error
		has_error = True
		log("错误：", msg)
	else:
		raise ExcelToCodeException(msg, file)

# 致命错误，无法被忽略
def log_fatal(msg, *args, **kargs):
	if len(args) > 0: msg = msg % args

	file = kargs and kargs.get("file")
	global has_error
	has_error = True
	log("错误：", msg)
	raise ExcelToCodeException(msg, file)

# 确保文件所在的路径存在。file_path是文件的路径。
def ensure_folder_exist(file_path):
	output_dir = os.path.dirname(file_path)
	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)

	return

# 确保file_path所经过的目录存在，并且存在__init__.py
def ensure_package_exist(root, file_path):
	sub_path = os.path.dirname(file_path)
	if os.path.isdir(os.path.join(root, sub_path)):
		return

	full_path = root
	paths = sub_path.replace('\\', '/').split('/')
	for path in paths:
		full_path = os.path.join(full_path, path)
		if os.path.isdir(full_path): continue

		os.mkdir(full_path)
		init_path = os.path.join(full_path, "__init__.py")
		with open(init_path, "w") as f:
			f.close()

	return

# src文件是否比dst文件更新
def if_file_newer(src, dst):
	t1, t2 = 0, 0
	try:
		t1 = os.path.getmtime(src)
		t2 = os.path.getmtime(dst)
	except OSError:
		return False

	return t1 > t2

# 收集path目录下所有后缀符合exts的文件。
# 返回的路径是相对于path的相对路径。
def gather_all_files(path, exts):
	ret = []
	path = path.decode("utf-8")

	path_len = len(path)
	if path[-1] != '/': path_len += 1

	for root, dirs, files in os.walk(path):
		i = 0
		while i < len(dirs):
			if dirs[i][0] == '.':
				dirs.pop(i)
			else:
				i += 1

		relative_path = root[path_len : ]

		for fname in files:
			if fname.startswith("~$"): continue

			ext = os.path.splitext(fname)[1]
			if ext not in exts: continue

			file_path = os.path.join(relative_path, fname)
			ret.append(file_path.encode("utf-8").replace('\\', '/'))

	return ret

def get_file_modify_time(file_path):
	return os.path.getmtime(file_path.decode('utf-8'))

# 将src目录递归的拷贝到dst目录。
# 与shutil.copytree不同之处在于，如果目标文件存在，会直接进行覆盖，而不是抛异常。
def copytree(src, dst, symlinks=False, ignore=None):
	names = os.listdir(src)
	if ignore is not None:
		ignored_names = ignore(src, names)
	else:
		ignored_names = set()

	if not os.path.isdir(dst):
		os.makedirs(dst)

	errors = []
	for name in names:
		if name in ignored_names:
			continue

		srcname = os.path.join(src, name)
		dstname = os.path.join(dst, name)
		if os.path.isdir(srcname):
			copytree(srcname, dstname, symlinks, ignore)
		else:
			shutil.copy2(srcname, dstname)

	return

# 如果目标文件夹已经存在，则不进行任何操作
def safe_mkdir(path, recreate = False):
	if recreate and os.path.exists(path):
		shutil.rmtree(path)
		os.mkdir(path)
	elif not os.path.exists(path):
		os.mkdir(path)

# 如果目标文件夹已经存在，则不进行任何操作
def safe_makedirs(path, recreate = False):
	if recreate and os.path.exists(path):
		shutil.rmtree(path)
		os.makedirs(path)
	elif not os.path.exists(path):
		os.makedirs(path)


def format_slash(path):
	return path.replace('\\', '/')


PATH_PATTERN = re.compile(r"\$\{?(\w+)\}?")

# 将路字符串中的${Macro}宏，替换为真实字符串。`Macro`是namespace数组中的任对象的属性名称
# eg. resolve_macro("${PROJECT_PATH}/sub/path", [xlsconfig, ])
def resolve_macro(name, namespace):
	ret = []

	start = 0
	while start < len(name):
		p = PATH_PATTERN.search(name, start)
		if p is None:
			ret.append(name[start:])
			break

		else:
			if p.start() != start:
				ret.append(name[start : p.start()])

			key = p.group(1)
			val = None
			
			for obj in namespace:
				if isinstance(obj, dict):
					val = obj.get(key)
				else:
					val = getattr(obj, key, None)
				if val is not None:
					break
			else:
				val = key

			ret.append(val)
			start = p.end()

	return "".join(ret)

def resolve_path(path, namespace = None):
	ns = namespace if namespace else (xlsconfig, )
	return os.path.normpath(resolve_macro(path, ns))

# 将json加载的字符串转换为utf-8
# https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json
def byteify(input):
	if isinstance(input, dict):
		return {byteify(key): byteify(value) for key, value in input.iteritems()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input


FORMAT_CHAR = {
	0	: '\\0',
	'\\' : '\\\\',
	'\n' : '\\n',
	'\r' : '\\r',
	'\b' : '\\b',
	'\t' : '\\t',
	'\f' : '\\f',
	'"'  : '\\"',
	"'"  : "\\'",
}
# 通用字符串格式化
def format_string(sting):
	ret = []
	for s in sting:
		ret.append(FORMAT_CHAR.get(s, s))
	return "".join(ret)

TRANSLATE_CHAR = {
	'0' : '\0',
	'\\' :  '\\',
	'n' : '\n',
	'r' : '\r',
	'b' : '\b',
	't' : '\t',
	'f' : '\f',
	'"' : '"' ,
	"'" : "'" ,
}
# 通用字符串转义
def translate_string(sting):
	if '\\' not in sting:
		return sting

	ret = []
	i = 0
	n = len(sting)
	while i < n:
		ch = sting[i]
		i += 1
		if ch == '\\' and i < n:
			next = TRANSLATE_CHAR.get(sting[i])
			if next:
				i += 1
				ch = next
		ret.append(ch)

	return "".join(ret)


class Watcher(object):
	def __init__(self, name):
		self.name = name
		self.begin_time = time.time()

	def stop(self):
		self.end_time = time.time()

	def report(self):
		log("%s 耗时 %.2fs" % (self.name, self.end_time - self.begin_time))
