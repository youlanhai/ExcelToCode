
MODULE_NAMES = (
	"tp0",
)

TYPE_MODULES = []

for name in MODULE_NAMES:
	module = __import__(name, globals(), locals(), [name, ])
	TYPE_MODULES.append(module)
