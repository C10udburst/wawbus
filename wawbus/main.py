# -*- coding: utf-8 -*-
from os.path import isfile
from queue import Queue
from threading import Thread
from time import sleep
from typing import Optional

import pandas as pd

from .api import ZtmApi, ZtmApiException
from .util.velocity_calc import speed

_DATASET_URL = "https://github.com/C10udburst/wawbus-data/raw/master/bus-data/{}.gzip"


class WawBus:
    api: Optional[ZtmApi] = None
    tt: Optional[pd.DataFrame] = None
    dataset: pd.DataFrame = pd.DataFrame()
    tt_worker_count: int = 5

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

        if dataset:
            if isfile(f"{dataset}.gzip"):
                self.dataset = pd.read_parquet(f"{dataset}.gzip")
            else:
                # download dataset
                self.dataset = pd.read_parquet(_DATASET_URL.format(dataset))

    def collect_positions(self, count: int, sleep_between: int = 10):
        if not self.api:
            raise ValueError("API key is required.")
        """
        Collect bus positions and append to dataset
        :return: None
        """
        dfs = [self.dataset]
        for i in range(count):
            print(f"Collecting data {i + 1}/{count}")
            try:
                response = self.api.get_bus_positions()
            except ZtmApiException as e:
                print(f"Error: {e}, skipping collection {i + 1}/{count}")
                sleep(sleep_between)
                continue
            df = pd.DataFrame(response, columns=[
                "Lat",
                "Lon",
                "Time",
                "Lines",
                "VehicleNumber",
                "Brigade"
            ])
            dfs.append(df)
            sleep(sleep_between)

        df = pd.concat(dfs, ignore_index=True)

        # for some fucking reason some entries have the year 2022024, so we need to coerce them
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df = df.dropna(subset=['Time'])

        self.dataset = df

    def calculate_speed(self) -> pd.DataFrame:
        """
        Calculate speed from dataset
        :return: A new dataframe with added column 'Speed'
        """
        df = self.dataset.copy(deep=False)
        df['NextLon'] = df.groupby('VehicleNumber')['Lon'].shift(-1)
        df['NextLat'] = df.groupby('VehicleNumber')['Lat'].shift(-1)
        df['NextTime'] = df.groupby('VehicleNumber')['Time'].shift(-1)

        df['Speed'] = df.apply(speed, axis='columns')

        df = df.drop('NextLat', axis=1)
        df = df.drop('NextLon', axis=1)
        df = df.drop('NextTime', axis=1)

        return df

    def _tt_worker(self, unprocessed: Queue, processed: Queue):
        while True:
            row = unprocessed.get()
            try:
                tt = self.api.get_timetable(stop_id=row['nr_zespolu'], stop_nr=row['nr_przystanku'], line=row['bus'])
            except ZtmApiException:
                # print(f"Error: {e}, skipping timetable {row['bus']}")
                unprocessed.task_done()
                continue
            for t in tt:
                t['bus'] = row['bus']
                t['nr_zespolu'] = row['nr_zespolu']
                t['nr_przystanku'] = row['nr_przystanku']
                processed.put(t)
            unprocessed.task_done()

    def _yield_timetables(self):
        """
        Fetches all timetables
        """

        unprocessed = Queue()
        processed = Queue()

        for _ in range(self.tt_worker_count):
            worker = Thread(target=self._tt_worker, args=(unprocessed, processed))
            worker.daemon = True
            worker.start()

        for row in self.api.get_routes():
            unprocessed.put(row)

        while unprocessed.qsize() > 0:
            if elem := processed.get():
                yield elem
                processed.task_done()

        unprocessed.join()

        while not processed.empty():
            yield processed.get()

    def collect_timetables(self):
        """
        Collect ALL timetables for all stops and set @code {self.tt}
        :return:
        """
        print("\033[1;31mThis will take a while\033[0m")

        df = pd.DataFrame(self._yield_timetables(), columns=[
            "bus",
            "nr_zespolu",
            "nr_przystanku",
            "brygada",
            "czas",
            "trasa"
        ], dtype=str)

        df['czas'] = pd.to_datetime(df['czas'], errors='coerce')
        df = df.dropna(subset=['czas'])

        self.tt = df
