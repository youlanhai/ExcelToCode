
MODULE_NAMES = (
	"tp0",
)

TYPE_MODULES = []

for name in MODULE_NAMES:
	module = __import__("tps." + name, globals(), locals(), [name, ])
	TYPE_MODULES.append(module)
