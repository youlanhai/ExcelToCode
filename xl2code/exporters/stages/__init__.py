
classes_name = (
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

classes = {}

for name in classes_name:
	module = __import__(name, globals(), locals(), [name, ])
	cls = getattr(module, name)
	classes[name] = cls
