导表工具
======================

Excel文件：
![](doc/excel.png)

转换后的python数据表：
```python
# 此文件由导表工具自动生成，禁止手动修改。
# from example.xlsx

# A ID                  编号
# B name                名称
# C describe            描述
# D quality             品质
main_sheet = {
    1: {"describe": "切菜用的", "name": "菜刀", "quality": 1, },
    2: {"name": "上方宝剑", "quality": 5, },
    3: {"name": "偃月弯刀", "quality": 0, },
}
```

# 原理
1. 搜索`excels`路径下的所有Excel文件
2. 根据`convention_table.py`中的Excel和`转换器`关系，找到Excel文件对应的转换器
3. 使用Excel文件和转换器作为参数，构造`xlsparser`
4. 第一阶段导表：parser将Excel数据转换成python表，存贮到中间目录下
5. 当所有文件转换完毕后，根据`convention_table.py`中的分表关系，将中间目录下的分表合成总表
6. 第二阶段导表：针对每个python表，执行深度类型转换，以及后处理操作。比如字段合并，生产新字段等。
7. 针对每个python表执行最后的数据合法性检查
8. 实例化writer对象，将python表转换成最终的python、lua、json等格式的数据表。

# 准备
+ python 2.7
+ 安装python插件openpyxl。使用`pip install openpyxl`安装，或者在config文件配置`DEPENDENCIES`项，指定openpyxl的安装包路径，导表工具会自动安装。

# 范例
见sample目录：

文件名称 | 描述
--------|---------
config.cfg | 导表工具配置文件
export.bat/export.sh | 导表批处理文件
post_init.py | 导表工具初始化完毕后回调。可以在脚本里做一些额外的初始化操作
excels | 存放excel文件所在目录。
converters | 转换器目录。
converters/convention_table.py | excel与转换器对应关系的描述文件
converters/converter | 转换器脚本

# 用法
## 如何执行导表？
```shell
python main.py --export your_configure_file
```

## 如何生成java类文件？
```shell
python main.py --gen-code your_configure_file
```

## 如何添加表头？
1. 在Excel表中，添加上“表头”，以及类型描述
2. 在转换器中的`CONFIG`字典中，添加上“表头”和代码中字段的对应关系，以及转换函数。

## 如何根据转换器配置为excel添加表头？
```shell
python main.py --gen-header your_configure_file
```

## 如何添加新Excel表？
1. 在`excels`路径下，新建Excel表，表内容格式如下：  

    行   | 描述
    ------|------
    第1行 | 预留
    第2行 | 预留
    第3行 | 表头
    第4行 | 基础类型描述。用于确定导表第一阶段数据类型。
    后续行 | 表格数据

    空白行或者列都是有效数据分割符，位于空白列右侧或空白行下侧，都会被导表工具忽略，因此可以存放注释或临时数据。

    通常**第1列**为数据的键值(key)。

2. 在`converter`目录下添加python转换器。转换器的详细写法，请参考`converter/example.py`。大致内容如下：
    ```python
    KEY_NAME = "ID"
    CONFIG = {
        ("编号", "ID", int),
        ("名称", "name", str),
        ("描述", "describe", str, True),
        ("品质", "quality", int, True, 0),
    }
    ```
    CONFIG是一个数组，描述了如何将excel表头转换成程序用的字段。

    数组索引 | 描述
    --------|------------
     0      | Excel表头文字
     1      | 程序使用的字段名
     2      | 转换函数。将excel表中的单元格转换成脚本对象。
     3      | 表示此列是否可缺省，即是否可不填。不指定表示为必填。
     4      | 缺省值。脚本中使用此值替代excel中没有填的位置，如果没有指定缺省值，脚本中就不会出现该单元格的数据。

3. 在`convention_table.py`文件中添加上Excel表与转换器的对应关系。
