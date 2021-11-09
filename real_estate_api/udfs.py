#!/usr/bin/env python
# -*-coding:utf-8 -*-
import re

from cn2an import cn2an
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType


@udf(returnType=IntegerType())
def convert_chinese_num(chinese_num):
    chinese_num = chinese_num[:-1]
    num = cn2an(chinese_num, "smart")

    return num


@udf()
def convert_time(time_str):
    time_pattern = "^(?P<year>\d+)(?P<month>\d{2})(?P<day>\d{2})$"
    match = re.search(time_pattern, time_str)
    if match:
        return "{year}-{month}-{day}".format(**match.groupdict())
