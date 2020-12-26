
classes_name = (
	"ParseExcel",
	"ConvertField",
	"ExtractConstant",
	"ExtractLocale",
	"MergeField",
	"MergeFiles",
	"MergeSheets",
	"PostCheck",
	"PostProcess",
	"RunCustomStage",
	"WriteConfigure",
	"WriteFileList",
	"WriteJavaFileEnum",
	"WriteJavaFileList",
	"WriteSheets",
)

CLASSES = {}

for name in classes_name:
	module = __import__("exporters.stages." + name, globals(), locals(), [name, ])
	cls = getattr(module, name)
	CLASSES[name] = cls
