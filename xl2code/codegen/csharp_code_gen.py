# -*- coding: utf-8 -*-
import util
import xlsconfig
from .base_code_gen import BaseCodeGen

BUILTIN_TYPES = set((
	"int", "long", "float", "boolean", "String",
))

TYPE_MAP = {
	"string" : "string",
	"text" : "string",
	"string_list" : "string[]",
	"int_list" : "int[]",
	"float_list" : "float[]",
	"boolean" : "bool",
	"point" : "Vector2",
	"point2" : "Vector2",
	"point3" : "Vector3",
	"vector3" : "Vector3",
	"timespan" : "float",
	"array<int>" : "int[]",
	"array<float>" : "float[]",
	"array<string>" : "string[]",
	"hexcolor" : "Color",
}

INDENTS = [" " * (i * 4) for i in range(10)]

class CSharpCodeGen(BaseCodeGen):

	def run(self):
		names = self.module_name.split('.')
		file_name = names.pop()
		file_dir = "/".join(names)

		self.class_name = util.to_class_name(file_name)

		generator_info = self.generator_info
		name_format = util.to_utf8(generator_info.get("name_format"))
		if name_format:
			self.class_name = name_format % self.class_name

		ns = {
			"FILE_DIR" : file_dir,
			"FILE_NAME" : self.class_name,
		}
		self.file_path = util.resolve_path(generator_info["file_path"], (ns, xlsconfig, ))
		util.ensure_folder_exist(self.file_path)

		self.write_line(0, "// 此文件由导表工具自动生成，禁止手动修改。")
		self.write_line()

		package = util.to_utf8(generator_info.get("package", xlsconfig.DEFAULT_JAVA_PACKAGE))

		imports = generator_info.get("imports")
		if imports:
			for imp in imports:
				self.write_line(0, "using %s;" % imp.encode("utf-8"))
			self.write_line()

		items = self.collect_members(self.module)

		indent = 0
		self.write_line(indent, "namespace ", package)
		self.write_line(indent, "{")

		indent += 1
		self.gen_class(items, indent)

		self.write_line()
		self.gen_sheet_class(indent)
		self.write_line()
		indent -= 1

		self.write_line()
		self.write_line(indent, "}")

		self.save_to_file(self.file_path)

	def collect_members(self, config):
		# info = (0, "ID", "编号", "int", )

		items = []
		for k, info in config.items():
			items.append(info)

		items.sort(key = lambda v: v[0])
		return items

	def gen_class(self, items, indent):
		self.write(indent, "public class ", self.class_name)

		base = self.generator_info.get("base")
		if base:
			self.output(" : ", base.encode("utf-8"))

		self.write_line()
		self.write_line(indent, "{")
		self.write_line()

		indent += 1
		self.gen_field_list(items, indent)
		indent -= 1

		self.write_line(indent, "}")

	def gen_field_list(self, items, indent):
		for item in items:
			col, name, comment, type = item

			type = TYPE_MAP.get(type.lower(), type)
			if type == "empty":
				self.write_line(indent, "/// %s %s" % (name, comment))
				continue

			self.write_line(indent, "/// " + comment)
			self.write_line(indent, "public %s %s;" % (type, name))
			self.write_line()

		self.write_line()

	def gen_sheet_class(self, indent):
		class_name = self.class_name + "Sheet"
		self.write_line(indent, '[SheetPath("%s")]' % self.module_name.replace('.', '/'))
		self.write_line(indent, "public class %s : SheetBase<%s>" % (class_name, class_name))
		self.write_line(indent, "{")

		indent += 1
		self.write_line(indent, "public Dictionary<int, %s> main_sheet;" % self.class_name)
		indent -= 1

		self.write_line(indent, "}")
