# -*- coding: utf-8 -*-
import os
from base_writer import BaseWriter
from struct import pack

def pack_debug(fmt, *args):
	return " ".join([str(x) for x in args]) + " "
# pack = pack_debug

MAGIC = "bt"
VERSION = 0x0001

T_EOF 		= 0 #end of file
T_NONE 		= 1
T_TRUE 		= 2
T_FALSE 	= 3
T_ZERO 		= 4
T_ONE 		= 5
T_INT8 		= 6
T_INT16 	= 7
T_INT32 	= 8
T_INT64 	= 9
T_FLOAT 	= 10
T_DOUBLE 	= 11
T_STR0 		= 12
T_STR8 		= 13
T_STR16 	= 14
T_STR32 	= 15
T_LIST0 	= 16
T_LIST8 	= 17
T_LIST16 	= 18
T_LIST32 	= 19
T_DICT0 	= 20
T_DICT8 	= 21
T_DICT16 	= 22
T_DICT32 	= 23
T_MAX 		= 24


INT8_MIN = -2**7
INT8_MAX = 2**7 - 1
INT16_MIN = -2**15
INT16_MAX = 2**15 - 1
INT32_MIN = -2**31
INT32_MAX = 2**31 - 1
INT64_MIN = -2**63
INT64_MAX = 2**63 - 1

def w_none(v):
	return pack("<B", T_NONE)

def w_bool(v):
	return pack("<B", T_TRUE if v else T_FALSE)

def w_int(v):
	if v == 0: return pack("<B", T_ZERO)
	if v == 1: return pack("<B", T_ONE)
	if INT8_MIN <= v <= INT8_MAX: return pack("<Bb", T_INT8, v)
	if INT16_MIN <= v <= INT16_MAX: return pack("<Bh", T_INT16, v)
	if INT32_MIN <= v <= INT32_MAX: return pack("<Bi", T_INT32, v)
	if INT64_MIN <= v <= INT64_MAX: return pack("<Bq", T_INT64, v)

	raise ValueError, "value is too large."

def w_float(v):
	return pack("<Bf", T_FLOAT, v)

def w_size(tp, size):
	if size == 0:    		return pack("<B",  tp + 0)
	if size <= 0xff:  		return pack("<BB", tp + 1, size)
	if size <= 0xffff: 		return pack("<BH", tp + 2, size)
	if size <= 0xffffffff: 	return pack("<BI", tp + 3, size)
	raise ValueError, "size is too large."

def w_str(l):
	return w_size(T_STR0, l)

def w_list(l):
	return w_size(T_LIST0, l)

def w_dict(l):
	return w_size(T_DICT0, l)


class BinaryWriter(BaseWriter):
	''' 输出二进制格式数据表
	格式(ebnf)：
	data = magic, version, string_pool, content
		magic = "bt"

		version = int16

		string_pool = pool_size, { string_size, string_data }
			pool_size = int32

			string_size = int16

		content = type, number | string_index | list | dict
			type = uint8

			number = int8 | int16 | int32 | int64 | float | double 

			string_index = uint of (type - T_STR0)

			list = list_size, { content }
				list_size = uint of (type - T_LIST0)

			dict = dict_size, { content, content }
				dict_size = uint of (type - T_DICT0)

	'''

	def open_file(self):
		self.handle = open(self.file_path, "wb")

	def flush(self):
		pass

	def begin_write(self):
		self.string_pool = {}
		self.var_dict = {}

	def end_write(self):
		# clear cache, and serialize var to cache
		self.cache = []
		self._write(self.var_dict)

		tail_cache = self.cache
		self.cache = []

		# write header first
		self.output(MAGIC)
		self.output(pack("<H", VERSION))

		# write string pool
		strings = [None] * len(self.string_pool)
		for s, i in self.string_pool.iteritems():
			strings[i - 1] = s

		self.output(pack("<I", len(strings)))
		for s in strings:
			self.output(pack("<H", len(s)))
			self.output(s)

		# append var data to cache tail
		self.cache.extend(tail_cache)

		# flush cache to file
		text = "".join(self.cache)
		self.cache = []
		self.handle.write(text)

	def write_types_comment(self, comments):
		pass

	def write_sheet(self, name, sheet):
		self.var_dict[name] = sheet

		if name == "main_sheet" and self.generator_info.get("record_keys"):
			self.write_value("main_length", len(sheet))

			keys = sheet.keys()
			keys.sort()
			self.write_value("main_keys", keys)

	def write_value(self, name, value):
		self.var_dict[name] = value

	def _write_str(self, value):
		if value == "":
			self.output(pack("<B", T_STR0))

		else:
			index = self.string_pool.get(value)
			if index is None:
				# NOTICE: index begin at 1
				index = len(self.string_pool) + 1
				self.string_pool[value] = index

			self.output(w_str(index))
		return

	def _write_key(self, value):
		tp = type(value)
		if tp == int or tp == long:
			self.output(w_int(value))

		elif tp == str:
			self._write_str(value)

		elif tp == unicode:
			self._write_str(value.encode("utf-8"))

		else:
			print value
			raise TypeError, "invalid key type %s" % (str(tp), )

	def _write(self, value):
		tp = type(value)
		if value is None:
			self.output(w_none(value))

		elif tp == bool:
			self.output(w_bool(value))

		elif tp == int or tp == long:
			self.output(w_int(value))

		elif tp == float:
			self.output(w_float(value))

		elif tp == str:
			self._write_str(value)

		elif tp == unicode:
			self._write_str(value.encode("utf-8"))

		elif tp == list or tp == tuple:
			self.output(w_list(len(value)))
			for v in value: self._write(v)

		elif tp == set:
			self._write(sorted(value))

		elif tp == dict:
			self.output(w_dict(len(value)))
			keys = value.keys()
			keys.sort()
			for k in keys:
				self._write_key(k)
				self._write(value[k])

		else:
			print value
			raise TypeError, "unsupported value type %s" % (str(tp), )

		return
