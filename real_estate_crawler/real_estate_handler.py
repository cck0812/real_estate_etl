#!/usr/bin/env python
# -*-coding:utf-8 -*-
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

        city_name = [
            key for key, val in constants.CITY_MAPPING_DICT.items() if val == city_code
        ][0]
        sale_purchase_type = [
            key
            for key, val in constants.SALE_PURCHASE_TYPE_MAPPING_DICT.items()
            if val == sale_purchase_code
        ][0]

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
    handler = RealEstateHandler()
    asyncio.run(handler.bulk_get_real_estate_data(108, 2))


if __name__ == "__main__":
    format = "%(asctime)s %(thread)d %(name)s %(levelname)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG)
    main()
