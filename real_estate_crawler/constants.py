#!/usr/bin/env python
# -*-coding:utf-8 -*-
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

ROOT_DIR = "/code"
DATA_DIR = os.path.join(ROOT_DIR, "data")

CITY_MAPPING_DICT = {"台北市": "A", "新北市": "B", "桃園市": "E", "台中市": "F", "高雄市": "H"}
SALE_PURCHASE_TYPE_MAPPING_DICT = {"不動產買賣": "A", "預售屋買賣": "B", "不動產租賃": "C"}
REAL_ESTATE_URL = "https://plvr.land.moi.gov.tw//DownloadSeason?season=%sS%s&fileName=%s_lvr_land_%s.%s"

CITY_LIST = ["台北市", "新北市", "桃園市", "台中市", "高雄市"]
SALE_PURCHASE_TYPE_LIST = ["不動產買賣"]
REQUEST_INTERVAL = 1


def get_city_code_list():
    city_code_list = [CITY_MAPPING_DICT.get(city_name) for city_name in CITY_LIST]
    return city_code_list


def get_sale_purchase_code_list():
    sale_purchase_code_list = [
        SALE_PURCHASE_TYPE_MAPPING_DICT.get(sale_purchase_type)
        for sale_purchase_type in SALE_PURCHASE_TYPE_LIST
    ]
    return sale_purchase_code_list


def get_real_estate_url(
    year, season, city_code, sale_purchase_code, file_extension="csv"
):
    dt_year = datetime.now().year - 1911
    if year > dt_year:
        year -= 1911

    return REAL_ESTATE_URL % (
        year,
        season,
        city_code,
        sale_purchase_code,
        file_extension,
    )
