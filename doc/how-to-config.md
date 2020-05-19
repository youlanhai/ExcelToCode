# 配置文件参数详解

```shell
# 执行导表
python main.py --export my_config.py
```

导表的时候，需要指定一个Python格式的配置文件，描述了导表过程中需要的一些参数。目前，导表工具支持3种表格配置方式：
1. 直接模式(DirectExporter)。在Excel表头中指定导出的字段名、字段类型，导表工具使用这些信息，生成数据字典。这种方式比较方便，但是不够灵活，不能对数据进行深度处理，比如字段合并、生成新字段。
2. 配置模式(ConfigExporter)。为每一种类型的Excel文件指定一个转换脚本，提供表头和数据的转换信息。这种方式支持数据深度处理，数据校验等。缺点是，要写为每一种类型的Excel都写一个脚本。
3. 混合模式(MixExporter)。混合模式结合了Direct和Config两种模式的优点，表头与Direct模式相同，不使用转换器也能完全工作。对于一些特殊类型，可以自己定义转换器脚本，进行处理。

**推荐使用混合模式**，即简单也灵活。

下面逐一介绍如何配置。

# 通用配置
注意，配置参数要区分大小写。路径相关的参数，都是相对路径，相对于当前的配置文件。

### post_init_method  
额外的初始化方法，执行一些自定义的初始化工作。比如修改配置，自定义代码注入等。
```python
def post_init_method():
    pass
```

### EXPORTER_CLASS  
执行导出逻辑的python类。目前可用的类有`DirectExporter`，`ConfigExporter`，`MixExporter`。这些类，位于`exporters`目录下。你也可以使用自定义的导出类，将类赋值给`exporters`模块，然后将`EXPORTER_CLASS`指定为你的类名字。

```python
EXPORTER_CLASS = "DirectExporter"
```

### INPUT_PATH
要转换的Excel文件所在目录。导表的时候，该目录及其子目录下的所有Excel文件都会被处理。因此，非数据相关的表，不要放到这里。**CONFIG_PATH**是当前配置文件所在的路径。

```python
INPUT_PATH = "${CONFIG_PATH}/excels"
```

### OUTPUT_PATH
该参数是一个辅助变量，方便配置文件内部使用。

```python
OUTPUT_PATH = "${CONFIG_PATH}/output"
```

### TEMP_PATH
中间文件路径。存放导表过程中生成的中间文件。如果导表的时候，指定了`--fast-mode`，这些中间文件会被复用。

```python
TEMP_PATH = "${CONFIG_PATH}/export/temp"
```

### DEFAULT_JAVA_PACKAGE
默认Java包名。只有生成Java相关代码的时候才有用。

```python
DEFAULT_JAVA_PACKAGE = "com.mygame.default.package"
```

### CODE_GENERATORS
代码生成器参数。`CODE_GENERATORS`是一个数组，可以指定多个生成器的参数。目前仅支持Java代码生成器。

```python
CODE_GENERATORS = [
    {
        "class" : "JavaCodeGen",
        "name_format" : "Dict%s",
        "file_path" : "${OUTPUT_PATH}/export/java/code/${FILE_PATH}.java",
        "imports" : ["com.mygame.test"],
        "interface" : "IInterface",
        "base" : "BaseClass",
    }
]
```

生成器参数 | 描述
---------|---------
class  | 生成器的类名。目前只支持生成Java类，你可以向codegen模块注册自定义的代码生成器类，然后在这里配置上。
file_path | 输出文件的路径。`FILE_PATH`参数由每个生成器自己给出，java生成器用的是excel的文件名称的驼峰法形式。
package | 为生成的Java类指定包名。如果不指定，则使用`DEFAULT_JAVA_PACKAGE`
imports | 为生成的Java类指定要导入的包。该参数是数组格式，支持导入多个包。如果不需要导入包，可忽略改参数。
base  | 为生成的Java类指定基类。如果没有基类，可忽略改参数。
interface | 为生成的Java类指定接口类。如果没有接口类，可忽略该参数。

### DATA_WRITERS
为输出数据表指定参数。`DATA_WRITERS`是一个数组，支持多个writer。writer类位于writers目录下，目前支持输出的数据表格式有Python、Lua、Json、JavaScript和Java专用的Json格式。可以自定义writer类，将自定义类赋值给`writers`模块。

```python
DATA_WRITERS = [
    {
        "stage" : 1,
        "class" : "LuaWriter",
        "file_path": "${OUTPUT_PATH}/export/lua/${FILE_PATH}.lua",
        "max_indent" : 2,
    }
]
```

writer参数 | 描述
----------|--------
stage   | 导表阶段。目前分两个阶段：Begin(1), Final(2)。Begin阶段的数据没有进行后处理。
class   | writer类。位于writers目录下。
file_path | 输出数据表的路径。
max_indent | 最大Tab缩进数

### EXPORTER_STAGES
定制化导表步骤。整个导表过程有很多阶段构成，依次向后执行。每个导出类(ExporterClass)有自己默认的步骤，这里可以通过配置`EXPORTER_STAGES`参数来使用自定义的导表步骤。每个阶段对应一个类，位于`exporters/stages`目录下，且需要注册到`exporters.classes`字典中。如下，是一个非常简单的导表阶段配置：

```python
EXPORTER_STAGES = [
    {"class" : "MergeSheets", },
    {"class" : "MergeField"},
    {"class" : "WriteSheets", "stage" : 1},
]
```

阶段名称 | 适用情况 | 描述
--------|---------|--------
BaseStage   |       | 阶段的基类
ConvertField | Mix  | 根据转换器提供的类型描述，再次转换字段的类型
MergeField  | Direct, Mix | 合并字段。根据表头field描述，将若干个字段合并成一个
MergeSheets | All   | 合并分表
PostProcess | Config, Mix | 根据脚本配置，执行后处理
PostCheck   | Config, Mix | 根据脚本配置，执行表格合法性检查
WriteSheets | All | 写出数据表
RunCustomStage | All| 执行额外的自定义的阶段。见`CUSTOM_STAGES`
WriteFileList | All | 写出文件列表
WriteConfigure | All| 写出一些表头的类型信息，以及合并参数

### CUSTOM_STAGES
自定义后处理阶段。在导表最后阶段调用，能够访问到exporter的所有数据。常用于生成文件列表。`CUSTOM_STAGES`是一个数组，支持配置多个阶段。阶段类位于`exporters/stages`目录下，目前支持生成Java文件映射表。关于导表阶段，见`EXPORTER_STAGES`

```python
CUSTOM_STAGES = [
    {
        "class" : "JavaFileEnumProcessor",
        "file_path" : "${OUTPUT_PATH}/export/java/excel/DictEnum.java"
    }
]
```


### DEPENDENCIES
Python插件安装包路径。目前导表工具依赖`openpyxl`。你可以指定插件的安装包路径，导表工具会自动检测插件是否存在，如果不存在会进行安装。方便为非技术人员使用。

```python
DEPENDENCIES = {
    "openpyxl" : "openpyxl-2.4.4.zip"
}
```

### ARGUMENT_CONVERTER
Excel表头参数解析，通常是针对Excel表的第一行。你可以在Excel中指定额外的信息，导表工具会分析出来，并存贮在中间模块中，其他的处理器可以访问到。这里提供了一些通用的参数，可以改变导表工具的行为。

```python
ARGUMENT_CONVERTER = {
    "版本：" : ["version", "int"],
    "键值是否重复：" : ["multiKey", "bool"],
    "说明：" : ["describe", "string"],
    "模板："  : ["template", "string"],
    "关联总表："  : ["mergeToSheet", "string"],
    "缩进：" : ["indent",    "int"],
}
```

类型 | 说明
------|------
模板  | 当前excel要使用的模板(或称为转换器)名称
关联总表 | 如果指定了该参数，当前表最终会合并到总表中
缩进  | 为输出文件指定缩进层级

### SHEET_ROW_INDEX
Excel表格数据所在行。索引从0开始，不填或填-1表示该行不存在。

```python
SHEET_ROW_INDEX = {
    # Excel表头参数。通常是版本信息和说明等，该行必须存在。
    "argument" : 0,
    # 表头。该行必须存在。
    "header" : 1,
    # 数据首行索引。该行必须存在。
    "data" : 2,
    # 字段。Direct模式下，该行必须存在
    "field" : -1,
    # 类型行。Direct模式下，该行必须存在
    "type" : -1,
    # 默认值所在行。如果某列没填，可以用此值替代
    "default"   : -1,
}
```

# Direct模式
Direct模式下，数据描述信息全部由Excel表提供。表格的行"argument"，"header"，"field"，"type"，"data"，都会使用到。

![](images/direct-header@2x.png)

# Config模式
Config模式下，数据描述信息有转换器脚本提供。因此，表头结构简单，但是需要提供额外的转换器脚本文件。

![](images/config-header@2x.png)

### CONVERTER_PATH
转换器所在的父级路径。

```python
CONVERTER_PATH = "converters"
```

### CONVERTER_ALIAS
转换器目录名，位于`CONVERTER_PATH`下。该目录存在的目的，只是为了防止命名冲突。

```python
CONVERTER_ALIAS = "converter"
```

### CONVENTION_TABLE
Excel与转换器对应关系表。每个数组元素也是一个数组，描述了Excel与转换器的对应关系。

```python
CONVENTION_TABLE = (
    ("example.xlsx", "example", ),
    (r"stage/normal/\d+/enemy.xlsx", "stage.enemy"), #-> stage/normal/\d+/enemy
    (r"(stage/normal/\d+/)enemy.xlsx", "stage.enemy", r"\1d_enemy", 0), #-> stage/normal/\d+/d_enemy
)
```

数组索引 | 描述
--------|------
 0      | 输入的Excel文件路径，路径相对于`INPUT_PATH`。**支持正则表达式**。
 1      | 转换器模块路径，路径相对于`CONVERTER_PATH/CONVERTER_ALIAS`。注意路径用符号'.'连接，而不是'/'。
 2      | 输出文件别名。支持**正则表达式替换**输入路径的名称。
 3      | excel文件的工作表索引。

### MERGE_TABLE
分表合并关系描述表。用来将几个分表合成一张总表。每个数组元素也是一个数组，0号位是合并后的文件名，1号位往后是要合并的文件名，支持正则表达式。注意，文件都不含后缀。
```python
MERGE_TABLE = (
    ("entity/entity", "entity/entity_subsheet", r"entity/entity_part\d+", ),
)
```

# Mix模式
Mix模式下，表头结构与Direct模式完全相同。同时也要配置转换器路径`CONVERTER_PATH`和`CONVERTER_ALIAS`，转换关系表可以不配置`CONVENTION_TABLE`。转换器的搜索规则如下：
1. 搜索`CONVENTION_TABLE`描述表
2. 在转换器目录下，搜索与输入文件**同路径**的python文件
3. 在转换器目录下，搜索与输入文件**同名**的python文件

Mix模式下，也支持分表合并，后处理操作。
