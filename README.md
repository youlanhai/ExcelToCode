导表工具
======================

Excel文件：
![](doc/images/direct-header@2x.png)

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
1. 构造exporter对象，开始整个导表流程
2. 搜索`INPUT_PATH`路径下的所有Excel文件
3. 构造parser对象，将Excel数据转换成python格式的中间数据表
4. 如果定义了后处理操作，exporter将对数据表执行后处理操作。比如表头合并，合法性检查
5. 实例化writer对象，将python表转换成最终的python、lua、json等格式的数据表。

# 准备
+ python 2.7
+ 安装python插件openpyxl。使用`pip install openpyxl`安装，或者在config文件配置`DEPENDENCIES`项，指定openpyxl的安装包路径，导表工具会自动安装。

# 工具用法
配置文件的写法，参考[表格格式配置](doc/how-to-config.md)

```shell
python main.py --export your_configure_file
```

main导表参数 | 说明
------------|--------
config_file | json格式的配置文件。配置文件的详细写法，参考[表格格式配置](doc/how-to-config.md)
--gen-code  | 生成类代码，目前仅支持Java。需要在config文件中，指定代码生成器参数`CODE_GENERATORS`
--export    | 执行导表。
--fast-mode | 快速模式，仅重新解析最近修改过的Excel表。解析Excel表的过程非常慢，快速模式会使用已经生成的中间文件来避免二次解析Excel表。
--force-run | 出错后是否继续进行导表。常用于发现更多的错误。
--gen-header| 根据`转换器`描述信息，自动生成表头。

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

