#!/usr/bin/env python
# -*-coding:utf-8 -*-
import logging
import os
from glob import glob

from flask import Flask
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from udfs import convert_chinese_num, convert_time

logger = logging.getLogger(__name__)

app = Flask(__name__)

spark = (
    SparkSession.builder.master("spark://spark-master:7077")
    .appName("Real Estate API")
    .getOrCreate()
)

fp = "./data/108/Q2/"
fp_list = glob(os.path.join(fp, "*"))

merged_df = None

for fp in fp_list:
    fname = os.path.splitext(os.path.basename(fp))[0]
    city_name, sale_purchase_type = fname.split("_")

    df = spark.read.csv(fp, header=True)
    df = df.filter(df["鄉鎮市區"] != "The villages and towns urban district")
    df = df.dropna(subset=["總樓層數"]).withColumn("總樓層數", convert_chinese_num("總樓層數"))
    df = df.withColumn("城市", F.lit(city_name))

    if merged_df is None:
        merged_df = df
    else:
        merged_df = merged_df.union(df)


@app.route("/data/<district>/<total_floor_number>/<building_state>")
def base_data(district, total_floor_number, building_state):
    df = merged_df.filter(
        (F.col("鄉鎮市區") == district)
        & (F.col("總樓層數") == total_floor_number & (F.col("建物型態") == building_state))
    )
    return df.toJSON().first()


if __name__ == "__main__":
    # conf = SparkConf().setMaster("spark://spark-master:7077").setAppName(__name__)
    # sc = SparkContext(conf=conf)

    app.run(debug=True, host="0.0.0.0")
