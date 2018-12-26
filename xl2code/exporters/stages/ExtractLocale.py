# -*- coding: utf-8 -*-
import re
import os
import traceback
import util
import xlsconfig
from BaseStage import BaseStage

FIELD_PATTERN = re.compile(r".*(\b\w+)")

def get_field_name(content):
	match = FIELD_PATTERN.search(content)
	field = match.group(1) if match else ""
	return field

class ExtractLocale(BaseStage):
	
	@property
	def need_sort(self): return True

	def get_desc(self): return "提取本地化数据"

	def process(self, exporter):
		util.safe_makedirs(xlsconfig.LOCALE_OUTPUT_PATH, True)

		super(ExtractLocale, self).process(exporter)

	def process_sheet(self, data_module):
		types = data_module.info["sheet_types"]["main_sheet"]
		sheet = data_module.main_sheet
		
		# 名字转换规则
		#	 文件路径_key[_multiKey流水号]_field
		# 文件路径中的斜线转换成'.'
		# 如果是重复key模式，才有multiKey流水号

		outfile = data_module.info["outfile"]
		prefix = outfile

		merge_to_file = data_module.info.get("mergeToFile")
		if merge_to_file:
			prefix = "%s/%s" % (merge_to_file, os.path.basename(outfile))
			outfile = merge_to_file

		prefix = prefix.replace('/', '.').replace('\\', '.')

		multi_key = data_module.info.get("multi_key")

		keys = types.keys()
		keys.sort()

		fields = set()
		fields.add("")

		texts = []
		def extract_row_text(row, key, col, posfix):
			text = row[col]
			if text is None:
				return

			text = self.format_text(text)

			name = "%s_%s_%s" % (prefix, str(key), posfix)
			row[col] = name
			texts.append((name, text))

		for i, title in enumerate(keys):
			if not title.endswith(":locale"): continue

			type_info = types[title]
			col = type_info[0]
			field = get_field_name(type_info[1])
			# 如果field重复，要重新起名
			if field in fields:
				field = field + str(i)
			fields.add(field)

			if multi_key:
				for k, rows in sheet.iteritems():
					for i, row in enumerate(rows):
						extract_row_text(row, k, col, "%s_%s" % (field, i))
			else:
				for k, row in sheet.iteritems():
					extract_row_text(row, k, col, field)

		if len(texts) > 0:
			self.save_texts(texts, outfile)

		return

	def save_texts(self, texts, outfile):
		texts.sort(key = lambda v: v[0])

		fname = outfile.replace('/', '_').replace('\\', '_')
		file_path = os.path.join(xlsconfig.LOCALE_OUTPUT_PATH, fname + ".txt")

		with open(file_path, "a+") as f:
			for name, text in texts:
				f.write("%s\n%s\n" % (util.to_utf8(name), util.to_utf8(text)))

		return

	def format_text(self, text):
		return util.format_string(text)
