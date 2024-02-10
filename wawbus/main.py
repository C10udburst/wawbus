# -*- coding: utf-8 -*-
from os.path import isfile
from queue import Queue
from threading import Thread
from time import sleep
from typing import Optional

import numpy as np
import pandas as pd

from .api import ZtmApi, ZtmApiException
from .util.dist import speed, stop_dist
from .constants import _DATASET_URL, _TIMETABLE_URL, _STOPS_URL, BUS_LENGTH, M_TO_KM
from .util.time import timeint


class WawBus:
    """
    Main class for collecting and processing bus data

    Attributes:
        api (ZtmApi): ZtmApi instance
        tt (pd.DataFrame): Timetable dataframe
        stops (pd.DataFrame): Stop locations dataframe
        dataset (pd.DataFrame): Dataset of bus positions dataframe
        tt_worker_count (int): Number of timetable collection workers when collecting timetables
    """
    api: Optional[ZtmApi] = None
    tt: Optional[pd.DataFrame] = None
    stops: Optional[pd.DataFrame] = None
    dataset: pd.DataFrame = pd.DataFrame()
    tt_worker_count: int = 5

    def __init__(self, /, *,
                 apikey: Optional[str] = None,
                 dataset: Optional[str] = None,
                 retry_count: int = 3):
        """
        Args:
            apikey (str): API key for ZtmApi (optional)
            dataset (str): frozen dataset's name (optional)
            retry_count (int): number of retries when collecting data

        Raises:
            ValueError: when both apikey and dataset are not provided
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
        """
        Collect bus positions

        Args:
            count (int): - number of collections
            sleep_between (int): - time between collections

        Updates:
            self.dataset (pd.DataFrame): Dataset of bus positions dataframe

        Raises:
            ZtmApiException: when API returns an error more than self.retry_count times
            ValueError: when API key is not provided
            InvalidColumnName: when API returns an invalid column name
        """
        if not self.api:
            raise ValueError("API key is required.")

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

        Returns:
            A copy of self.dataset dataframe with new "Speed" column added.
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

    def calculate_late(self, tolerance: pd.Timedelta = pd.Timedelta('15 minutes')) -> pd.DataFrame:
        """
        Calculate how late buses are

        Args:
            tolerance (pd.Timedelta): time tolerance for merging timetable and dataset

        Returns:
            A union of dataset and timetable with new "dist" column added specifying distance to the stop the
            bus was supposed to be at.
        """
        self._lazyload_stops()
        self._lazyload_timetable()

        # tt_loc contains timetable with stop locations
        tt_loc = pd.merge(self.tt, self.stops, left_on=['nr_zespolu', 'nr_przystanku'], right_on=['zespol', 'slupek'])
        tt_loc = tt_loc.drop(columns=['zespol', 'slupek'])

        df = self.dataset.copy(deep=False)

        # calculate time as int, so it can be merged by closest time
        df['t'] = df['Time'].apply(timeint)
        tt_loc['t'] = tt_loc['czas'].apply(timeint)

        # merge by closest time, line and brigade
        # we do it this way, instead of merging by position
        # because we neither pandas nor geopandas support merging by closest point with extra condition
        # and we cant just filter it out later, because it doesn't fit in memory
        df = pd.merge_asof(
            df.sort_values('t'),
            tt_loc.sort_values('t'),
            left_on='t',
            right_on='t',
            direction='backward',
            left_by=['Lines', 'Brigade'],
            right_by=['bus', 'brygada'],
            tolerance=tolerance.seconds
        )
        df = df.drop(columns=['t', 'bus', 'brygada'])

        # calculate distance to stop
        df['dist'] = df.apply(stop_dist, axis='columns')
        df = df[df['dist'] >= (BUS_LENGTH * M_TO_KM)]  # filter out buses that are too close to the stop

        df = df.drop_duplicates()

        return df

    def _lazyload_timetable(self):
        if self.tt is not None:
            return
        url = _TIMETABLE_URL.format("weekday")  # TODO: make tt for each day of the week
        self.tt = pd.read_parquet(url)

    def _tt_worker(self, unprocessed: Queue, processed: Queue):
        """
        Timetable collection worker definition

        Args:
            unprocessed (Queue): Queue with dicts nr_zespolu, nr_przystanku, bus
            processed (Queue): Queue with timetable entries
        """
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
        Collect ALL timetables for all stops

        Updates:
            self.tt (pd.DataFrame): Timetable dataframe

        Raises:
            ValueError: when API key is not provided
        """
        if not self.api:
            raise ValueError("API key is required.")

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

    def _lazyload_stops(self):
        if self.stops is not None:
            return
        self.stops = pd.read_parquet(_STOPS_URL)

    def collect_stops(self):
        """
        Collect stop positions

        Updates:
            self.stops (pd.DataFrame): Stop locations dataframe

        Raises:
            ValueError: when API key is not provided
            ZtmApiException: when API returns an error more than self.retry_count times
            InvalidColumnName: when API returns an invalid column name
        """
        if not self.api:
            raise ValueError("API key is required.")

        self.stops = pd.DataFrame(self.api.get_stop_locations(), columns=[
            "zespol", "slupek", "szer_geo", "dlug_geo"
        ])

        self.stops['szer_geo'] = self.stops['szer_geo'].astype(np.float64)
        self.stops['dlug_geo'] = self.stops['dlug_geo'].astype(np.float64)
