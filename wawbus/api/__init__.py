# -*- coding: utf-8 -*-
from typing import Optional

import requests

from .exceptions import ZtmApiException, ZtmHttpException


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
            if isinstance(result, list):
                return result
            elif isinstance(result, str):
                raise ZtmApiException(result)
            else:
                raise ZtmApiException('Unknown result type')
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

    def get_bus_positions(self):
        """
        Get bus positions
        :return: response
        """
        return self._req(
            'busestrams_get',
            'f2e5503e-927d-4ad3-9500-4ab9e55deb59',
            type='1'
        )

    def get_routes(self):
        """
        Get bus routes
        :return: response
        """
        return self._req(
            'public_transport_routes'
        )
