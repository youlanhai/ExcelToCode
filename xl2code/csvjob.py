# -*- coding: utf-8 -*-
#
# 批量转换excel文件为csv
#
from os import path
import subprocess
import json
import time

import xlsconfig
import util

class CSVJob(object):

	def __init__(self, input_path, output_path, temp_path, job):
		self.input_path = input_path
		self.output_path = output_path
		self.temp_path = temp_path

		assert job > 0
		self.job = job

	def run(self):
		self.load_cache_file()
		self.parse_files()
		self.save_cache_file()

	def load_cache_file(self):
		self.parser_cache = {}
		cache_file = path.join(self.temp_path, "cache.json")
		try:
			with open(cache_file, "r") as f:
				self.parser_cache = json.load(f, object_hook = util.byteify)
		except:
			pass

	def save_cache_file(self):
		cache_file = path.join(self.temp_path, "cache.json")

		content = json.dumps(self.parser_cache, ensure_ascii = False, indent = 4, sort_keys = True)
		with open(cache_file, "w") as f:
			f.write(content)

	def record_file(self, fname):
		self.parser_cache[fname] = {
			"createTime" : time.time(),
		}

	def collect_files(self, input_path):
		files = util.gather_all_files(input_path, (".xlsx", ))
		util.log("发现excel文件数量：", len(files))

		# 移除没有修改的文件
		if xlsconfig.FAST_MODE:
			i = len(files) - 1
			while i >= 0:
				fname = files[i]
				file_path = path.join(input_path, fname)
				parse_info = self.parser_cache.get(fname)
				if parse_info and parse_info.get("createTime", 0) > util.get_file_modify_time(file_path):
					files.pop(i)
				i -= 1

		util.log("需要导出的excel数量：", len(files))
		return files

	def parse_files(self):
		files = self.collect_files(self.input_path)
		if len(files) == 0:
			return

		job = min(self.job, len(files))

		group_count = len(files) // job
		processes = []
		for i in xrange(job):
			start = i * group_count
			end = start + group_count if i + 1 < job else len(files)
			section = files[start : end]

			config_file = path.join(self.temp_path, "job-%d.txt" % i)
			with open(config_file, "wb") as f:
				for name in section:
					f.write(name)
					f.write('\n')

			args = [
				"python",
				xlsconfig.CSV_CONVERTER,
				"-o", self.output_path,
				"-c", config_file,
				self.input_path,
				"-v",
			]
			if xlsconfig.EXPORT_ALL_WORKSHEET:
				args.append("-a")

			util.log_verbose("start process: ", " ".join(args))
			p = subprocess.Popen(args)
			processes.append(p)

		has_error = False
		for i, p in enumerate(processes):
			p.wait()
			ret = p.returncode
			if ret != 0:
				util.log("subprocess[%d] exit with error: %d" % (i, ret))
				has_error = True
			else:
				util.log("subprocess[%d] exit." % (i, ))

		if has_error:
			raise util.ExcelToCodeException, "转换csv失败"

		for fname in files:
			self.record_file(fname)

		return
