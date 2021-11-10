#!/usr/bin/env python
# -*-coding:utf-8 -*-
import logging
import os
from glob import glob

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from udfs import convert_chinese_num, convert_time

logger = logging.getLogger(__name__)


class SparkSQLTransformer:
    def __init__(self, session=None, master_url=None, app_name=None, target_path=None):
        self.session = session
        self.master_url = master_url
        self.app_name = app_name
        self.target_path = target_path

        self.merged_df = None

    def init_session(self):
        master_url = "local[*]" if self.master_url is None else self.master_url
        app_name = "Real Estate App" if self.app_name is None else self.app_name

        self.session = (
            SparkSession.builder.master(master_url).appName(app_name).getOrCreate()
        )

    def transform(self, df, fp):
        """
        :param spark dataframe df: A spark dataframe needs to be transformed
        :param string fp: A file path
        :return: A spark dataframe
        """

        fname = os.path.splitext(os.path.basename(fp))[0]
        city_name, sale_purchase_type = fname.split("_")

        # Drop irrelevant data
        df = df.filter(df["鄉鎮市區"] != "The villages and towns urban district")

        # Transform chinese numbers to arabic numbers
        df = df.dropna(subset=["總樓層數"]).withColumn("總樓層數", convert_chinese_num("總樓層數"))

        # Add city name column to dataset
        df = df.withColumn("縣市", F.lit(city_name))

        return df

    def get_and_merge_df(self, target_path):
        """Read CSV data from target path and merge all the dataset"""

        merged_df = None
        fp_list = glob(os.path.join(target_path, "*"))

        for fp in fp_list:
            df = self.session.read.csv(fp, header=True)
            df = self.transform(df, fp)

            if merged_df is None:
                merged_df = df
            else:
                merged_df = merged_df.union(df)

        self.merged_df = merged_df

    def filter_by_conditions(self, conditions):
        if self.session is None:
            self.init_session()

        if self.merged_df is None:
            self.get_and_merge_df(self.target_path)

        filtered_df = self.merged_df.filter(eval(conditions))
        return filtered_df

    def output_to_json(self):

        self.merged_df = self.merged_df.filter(
            (F.col("主要用途") == "住家用")
            & (F.col("建物型態").startswith("住宅大樓"))
            & (F.col("總樓層數") >= 13)
        )
        self.merged_df = self.merged_df.select(
            "鄉鎮市區", "交易年月日", "建物型態", "城市"
        ).withColumn("交易年月日", convert_time("交易年月日"))

        rename_columns = ["district", "date", "building_state", "city"]
        for old, new in zip(self.merged_df.columns, rename_columns):
            self.merged_df = self.merged_df.withColumnRenamed(old, new)


def main():
    pass


if __name__ == "__main__":
    main()
