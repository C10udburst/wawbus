# -*- coding: utf-8 -*-
from typing import Optional
import pandas as pd
from time import sleep

from wawbus.api import ZtmApi, ZtmApiException


class WawBus:
    api: Optional[ZtmApi] = None

    def __init__(self, /, *,
                 apikey: Optional[str] = None,
                 dataset: Optional[str] = None,
                 retry_count: int = 3):
        """
        :param apikey: api.um.warszawa.pl API key
        :param dataset: frozen dataset name
        """

        if not apikey and not dataset:
            raise ValueError("API key or dataset is required.")

        if apikey:
            self.api = ZtmApi(apikey, retry_count)
        self.dataset = dataset

    def collect_positions(self, count: int, sleep_between: int = 10):
        if not self.api:
            raise ValueError("API key is required.")
        """
        Collect bus positions
        :return: response
        """
        dfs = []
        for i in range(count):
            print(f"Collecting data {i+1}/{count}")
            try:
                response = self.api.get_bus_positions()
            except ZtmApiException as e:
                print(f"Error: {e}, skipping collection {i+1}/{count}")
                sleep(sleep_between * 2)
                continue
            df = pd.DataFrame(response)
            dfs.append(df)
            sleep(sleep_between)

        df = pd.concat(dfs, ignore_index=True)

        df['Time'] = pd.to_datetime(df['Time'])

        return df
