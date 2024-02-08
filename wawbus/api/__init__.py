# -*- coding: utf-8 -*-
from typing import Optional, List

import requests

from .exceptions import ZtmApiException, ZtmHttpException


def _normalize_kv(data: List[dict]) -> List[dict]:
    """
    Normalize key-value pairs
    :param data: list in api.um.warszawa.pl format
    :return: response a list of proper keys
    """
    return [{x['key']: x['value'] for x in d['values']} for d in data]


class ZtmApi:
    api_key: str
    retry_count: int = 3

    def __init__(self, api_key: str, retry_count: int = 3):
        self.api_key = api_key
        self.retry_count = retry_count

    def _req_once(self, endpoint: str, rid: Optional[str] = None, **qparams):
        """
        Generic request method for ZTM API
        :param endpoint: which endpoint to use
        :param rid: resource id
        :param kwargs: other query parameters
        :return: response
        """
        qparams['apikey'] = self.api_key
        if rid:
            qparams['resource_id'] = rid

        try:
            r = requests.get(
                f'https://api.um.warszawa.pl/api/action/{endpoint}',
                params=qparams
            )
        except requests.exceptions.RequestException as e:
            raise ZtmHttpException(e)

        if r.status_code != requests.codes.ok:
            raise ZtmApiException(f'API error: {r.status_code}')
        else:
            response = r.json()

        if error := response.get('error'):
            raise ZtmApiException(error)

        if result := response.get('result'):
            if isinstance(result, str):
                raise ZtmApiException(result)
            else:
                return result
        else:
            raise ZtmApiException('No result in response')

    def _req(self, endpoint: str, rid: Optional[str] = None, **qparams):
        """
        Request method with retries
        :param endpoint: which endpoint to use
        :param rid: resource id
        :param kwargs: other query parameters
        :return: response
        """
        err = None
        for _ in range(self.retry_count):
            try:
                return self._req_once(endpoint, rid, **qparams)
            except ZtmApiException as e:
                err = e
        else:
            raise err

    def get_bus_positions(self) -> List[dict]:
        """
        Get bus positions
        :return: response a list of dicts with keys: Lat, Lon, Time, Lines, VehicleNumber, Brigade
        """
        return self._req(
            'busestrams_get',
            'f2e5503e-927d-4ad3-9500-4ab9e55deb59',
            type='1'
        )

    def get_routes(self) -> List[dict]:
        """
        Get bus routes
        :return: response a list of dicts with keys: odleglosc, ulica_id, nr_zespolu, typ, nr_przystanku, bus,
        direction, stop
        """
        for bus, data in self._req(
                'public_transport_routes'
        ).items():
            for direction, stops in data.items():
                for stop, kv in stops.items():
                    kv['bus'] = bus
                    kv['direction'] = direction
                    kv['stop'] = stop
                    yield kv

    def get_stop_locations(self) -> List[dict]:
        """
        Get bus stop locations
        :return: response a list of dicts with keys: zespol, slupek, nazwa_zespolu, id_ulicy, szer_geo, dlug_geo,
        kierunek, obowiazuje_od
        """
        return _normalize_kv(self._req(
            'dbstore_get',
            id='ab75c33d-3a26-4342-b36a-6e5fef0a3ac3'
        ))

    def get_timetable(self, stop_id: str, line: str, stop_nr: str) -> List[dict]:
        """
        Get bus timetable
        :param stop_id: bus stop id
        :param line: bus line number
        :param stop_nr: bus stop number
        :return: response a list of dicts with keys: symbol_2, symbol_1, brygada, kierunek, trasa, czas
        """
        return _normalize_kv(self._req(
            'dbtimetable_get',
            id='e923fa0e-d96c-43f9-ae6e-60518c9f3238',
            busstopId=stop_id,
            busstopNr=stop_nr,
            line=line
        ))
