#!/usr/bin/env python
# -*-coding:utf-8 -*-
import logging
import os
from glob import glob

from flask import Flask
from pyspark import SparkConf, SparkContext
from pyspark.sql import functions as F

from constants import DATA_DIR
from transformer import SparkSQLTransformer

logger = logging.getLogger(__name__)

app = Flask(__name__)

spark_transformer = SparkSQLTransformer(target_path=DATA_DIR)


@app.route("/data/<district>/<total_floor_number>/<building_state>")
def filter_data(district, total_floor_number, building_state):
    conditions = f'(F.col("鄉鎮市區") == {district!r}) & (F.col("總樓層數") == {total_floor_number!r}) & (F.col("建物型態").startswith({building_state!r}))'
    filtered_df = spark_transformer.filter_by_conditions(conditions)

    if filtered_df.rdd.isEmpty():
        return "There's no data !"
    else:
        return filtered_df.toJSON().first()


if __name__ == "__main__":
    # conf = SparkConf().setMaster("spark://spark-master:7077").setAppName(__name__)
    # sc = SparkContext(conf=conf)

    app.run(debug=True, host="0.0.0.0")
