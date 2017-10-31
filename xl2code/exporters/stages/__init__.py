
classes_name = (
	"ConvertField",
	"MergeField",
	"MergeSheets",
	"MergeFiles",
	"PostCheck",
	"PostProcess",
	"RunCustomStage",
	"WriteConfigure",
	"WriteFileList",
	"WriteSheets",
	"WriteJavaFileEnum",
	"WriteJavaFileList",
)

classes = {}

for name in classes_name:
	module = __import__(name, globals(), locals(), [name, ])
	cls = getattr(module, name)
	classes[name] = cls
