# -*- coding: utf-8 -*-
from BaseStage import BaseStage
from writers import BaseWriter

import os
import util
import xlsconfig

def to_enum_name(name):
	return name.replace('/', '_').replace('\\', '/').upper()

class WriteJavaFileEnum(BaseStage):

	def process(self, exporter):
		info = self.info

		file_path = util.resolve_path(info["file_path"])
		util.ensure_folder_exist(file_path)
		util.log("生成枚举类", file_path)

		wt = BaseWriter(file_path, None)

		indent = 0
		wt._output_line(indent, "// 此文件由导表工具自动生成，禁止手动修改。")
		wt._output_line()

		package = util.to_utf8(info.get("package", xlsconfig.DEFAULT_JAVA_PACKAGE))
		wt._output_line(indent, "package %s;" % package)
		wt._output_line()

		class_name = os.path.splitext(os.path.basename(file_path))[0]
		wt._output_line(indent, "public enum %s {" % class_name)
		indent += 1

		value_pairs = []
		for outfile, data_module in exporter.data_modules.iteritems():
			enume_name = to_enum_name(outfile)
			comment = data_module.info["arguments"].get("describe")
			value_pairs.append((enume_name, comment))

		value_pairs.sort(key = lambda v : v[0])

		for enum_name, comment in value_pairs:
			if comment:
				wt._output_line(indent, "%-20s // %s" % (enum_name + ",", comment))
			else:
				wt._output_line(indent, enum_name, ",")

		indent -= 1
		wt._output_line(indent, "};")

		wt.close()
