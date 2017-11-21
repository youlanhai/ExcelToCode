
# 简单导表
有时需要单独处理一个excel表，比如处理sheet页提取信息。用下面的方法，可以快速导出一个excel为python数据表。

```python
from parsers.direct_parser import DirectParser
from exporters.stages.MergeField import MergeField

# 构造excel解析器
parser = DirectParser(excel_file_path, None)
parser.run()

my_sheet = parser.sheet

# 合并表格字段。将数组转换成哈希表
stage = MergeField(None)
stage.convert_sheet(my_sheet, parser.sheet_types, parser.is_multi_key)
```
