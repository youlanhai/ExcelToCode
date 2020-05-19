导表工具
======================

项目主页：https://github.com/youlanhai/ExcelToCode

Excel文件：
![](doc/images/direct-header@2x.png)

转换后的python数据表：
```python
# -*- coding: utf-8 -*-
# 此文件由导表工具自动生成，禁止手动修改。
# from example.xlsx

# A ID                  编号
# B name                名称
# C describe            描述
# D quality             品质
# E drop                掉落关卡
main_sheet = {
    1: {"describe": "切菜用的", "drop": [1, 2, 3, 4, ], "name": "菜刀", "quality": 1, },
    2: {"drop": [2, ], "name": "上方宝剑", "quality": 5, },
    3: {"name": "偃月弯刀", "quality": 0, },
}
```

# 原理
1. 构造exporter对象，开始整个导表流程
2. 搜索`INPUT_PATH`路径下的所有Excel文件
3. 构造parser对象，将Excel数据转换成python格式的中间数据表
4. 如果定义了后处理操作，exporter将对数据表执行后处理操作。比如表头合并，合法性检查
5. 实例化writer对象，将python表转换成最终的python、lua、json等格式的数据表。

# 准备
+ python 2.7
+ 安装python插件openpyxl。使用`pip install openpyxl`安装，或者在config文件配置`DEPENDENCIES`项，指定openpyxl的安装包路径，导表工具会自动安装。

# 工具用法

```shell
python main.py --export your_configure_file
```

main导表参数 | 说明
------------|--------
config_file | python格式的配置文件。配置文件的详细写法，参考[配置文件参数详解](doc/how-to-config.md)
--gen-code  | 生成类代码，目前仅支持Java。需要在config文件中，指定代码生成器参数`CODE_GENERATORS`
--export    | 执行导表
--fast-mode | 快速模式，仅重新解析最近修改过的Excel表。解析Excel表的过程非常慢，快速模式会使用已经生成的中间文件来避免二次解析Excel表
--force-run | 出错后是否继续进行导表。常用于发现更多的错误
--gen-header| 根据`转换器`描述信息，自动生成表头

# 范例
见`samples`目录。`direct-mode`目录下的例子使用的是*直接模式(Direct)*，`config-mode`目录下的例子使用的是*配置模式(Config)*，`mix-mode`目录下的例子使用的是*混合模式(Mix)*。

文件名称 | 描述
--------|---------
config.py | 导表工具配置文件
export.bat/export.sh | 导表批处理文件
excels | 存放excel文件所在目录
converters | 转换器父级目录
converters/converter | 转换器脚本存放路径

# 文档
1. [配置文件参数详解](doc/how-to-config.md)
2. [表格添加方法](doc/how-to-create-excel.md)
3. [简单导表](doc/easy-export.md)

# 路径说明
路径 | 说明
------|-------
doc | 文档
samples | 一些例子
xl2code | 导表工具源码
xl2code/codegen | 代码生成器。如，生成Java代码
xl2code/exporters | 导出器。用于将excel表转换成相应的数据结构
xl2code/exporters/stages | 导表阶段。可以定制化导表过程。比如，移动文件目录，生成额外的文件列表等
xl2code/parsers | excel解析器。解析单个excel表格
xl2code/tps | 通用类型转换器。用于将数据转换成具体的Python数据类型
xl2code/writers | 写出器。用于将Python数据表，写出成不同格式的数据表。如，Lua、Json等。
xl2csv | excel表转换成csv表的工具
xl2header | excel与表头描述文件互转的工具
