# -*- coding: utf-8 -*-
import util

class DataModule(object):
	def __init__(self, path, info, sheet, converter = None):
		super(DataModule, self).__init__()
		self.path = path
		self.info = info
		self.main_sheet = sheet
		self.converter = converter

class NewConverter(object):
	def __init__(self, name, types, arguments, filename):
		super(NewConverter, self).__init__()
		self.name = name
		self.types = types
		self.arguments = arguments
		self.filename = filename

	def compare_types(self, types, filename):
		for k, info1 in self.types.iteritems():
			info2 = types.get(k)
			if info2 and self.if_info_equal(info1, info2): continue

			util.log_error("'%s':'%s'与'%s':'%s'表头不一致", filename, info2, info1, self.filename)
			return False
		return True

	def if_info_equal(self, info1, info2):
		for i in xrange(1, 4):
			if info1[i] != info2[i]:
				return False
		return True
