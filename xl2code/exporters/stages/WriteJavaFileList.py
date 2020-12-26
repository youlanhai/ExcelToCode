# -*- coding: utf-8 -*-
import os
import xlsconfig
from writers import JsonWriter
import util
from util import to_utf8, to_class_name, format_slash
from .BaseStage import BaseStage

class WriteJavaFileList(BaseStage):

	def process(self, exporter):
		info = self.info

		file_path = util.resolve_path(info["file_path"])
		util.ensure_folder_exist(file_path)
		util.log("生成文件列表", file_path)

		only_name = os.path.splitext(os.path.basename(file_path))[0]

		wt = JsonWriter(file_path, None)
		wt.begin_write()

		package = to_utf8(info.get("package", xlsconfig.DEFAULT_JAVA_PACKAGE))
		wt.write_value("package", to_utf8(package))

		class_name_format = to_utf8(info.get("class_name_format"))
		enum_name_format = to_utf8(info.get("enum_name_format"))

		keys = list(exporter.data_modules.keys())
		keys.sort()

		ret = []
		for key in keys:
			data_module = exporter.data_modules[key]
			converter_name = data_module.info["parser"]

			file_name = os.path.splitext(key)[0]

			enum_name = file_name.replace('\\', '_').replace('/', '_').upper()
			if enum_name_format:
				enum_name = enum_name_format % enum_name

			fpath, fname = os.path.split(file_name)
			file_name = os.path.join(only_name, fpath, "%s.wg" % fname)
			file_name = format_slash(file_name)

			class_name = to_class_name(converter_name.split('.')[-1])
			if class_name_format:
				class_name = class_name_format % class_name

			ret.append([enum_name, file_name, class_name])

		wt.write_value(only_name, ret)

		wt.end_write()
		wt.close()
