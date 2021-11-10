#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""Handle real estate data from https://plvr.land.moi.gov.tw/DownloadOpenData"""
import argparse
import asyncio
import itertools
import logging
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import aiofiles
from requests_html import AsyncHTMLSession

import constants

logger = logging.getLogger(__name__)


class RealEstateHandler:
    def __init__(self):
        self.data_dir = constants.DATA_DIR

    @property
    def asession(self):
        return AsyncHTMLSession()

    def get_target_urls(self, year, season):
        """
        Get url list for crawling

        :param int year: Year of real estate data
        :param int season season: Season of real estate data
        :return: Valid real estate urls
        :rtype Generator
        """
        city_code_list = constants.get_city_code_list()
        sale_purchase_code_list = constants.get_sale_purchase_code_list()

        # Get all combination of city_code and sale_purchase_code
        city_sale_purchase_comb = itertools.product(
            city_code_list, sale_purchase_code_list
        )
        for city_code, sale_purchase_code in city_sale_purchase_comb:
            yield constants.get_real_estate_url(
                year, season, city_code, sale_purchase_code
            )

    async def crawl_url(self, url, **kwargs):
        """
        Async request to crawl concurrently

        :param string url: A valid real estate url
        :param **kwargs: Parameters of request method
        :return: Response from url
        :rtype HTMLResponse
        """
        await asyncio.sleep(constants.REQUEST_INTERVAL)

        resp = await self.asession.get(url, **kwargs)
        resp.raise_for_status()

        return resp

    async def save_data(self, year, season, url, content):
        season = "Q%s" % season
        year = str(year)

        f_dir_path = Path(os.path.join(self.data_dir, year, season))
        f_dir_path.mkdir(parents=True, exist_ok=True)  # Create dir if doesn't exist
        fname = self._get_fname_from_url(url)

        async with aiofiles.open(os.path.join(f_dir_path, fname), mode="wb") as f:
            await f.write(content)

        logger.info(f"Downloaded {year}{season} real estate data: {fname}")

    def _get_fname_from_url(self, url):
        parsed_url = urlparse(url)
        captured_value = parse_qs(parsed_url.query)
        fname = captured_value["fileName"][0]

        fn_noext, ext = os.path.splitext(fname)
        city_code = fn_noext[0]
        sale_purchase_code = fn_noext[-1]

        # Find actual city name in the mapping dictionary
        city_name = [
            key for key, val in constants.CITY_MAPPING_DICT.items() if val == city_code
        ][0]
        # Find actual sale and purchase type in the mapping dictionary
        sale_purchase_type = [
            key
            for key, val in constants.SALE_PURCHASE_TYPE_MAPPING_DICT.items()
            if val == sale_purchase_code
        ][0]

        # Reformat file name and add 'city name', 'sale and purchase type' dimensions
        fname = f"{city_name}_{sale_purchase_type}{ext}"

        return fname

    async def get_real_estate_data(self, year, season, url, **kwargs):
        resp = await self.crawl_url(url, **kwargs)
        await self.save_data(year, season, url, resp.content)

    async def bulk_get_real_estate_data(self, year, season, **kwargs):
        target_urls = self.get_target_urls(year, season)
        tasks = []
        for url in target_urls:
            tasks.append(self.get_real_estate_data(year, season, url, **kwargs))

        try:
            await asyncio.gather(*tasks)
        except Exception as err:
            logger.error(err)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "year",
        nargs="?",
        type=int,
        help="Assign a chinese era name of year, e.g., 109, 110",
    )
    arg_parser.add_argument(
        "season",
        nargs="?",
        type=int,
        help="Assign a season, e.g., 1, 2, 3, 4",
    )
    args = arg_parser.parse_args()

    year, season = args.year, args.season
    if year is None or season is None:
        logger.warning("Please assign both year and season arguments !")

    else:
        try:
            handler = RealEstateHandler()
            asyncio.run(handler.bulk_get_real_estate_data(year, season))
        except Exception as err:
            logger.error(err)


if __name__ == "__main__":
    format = "%(asctime)s %(thread)d %(name)s %(levelname)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG)
    main()
