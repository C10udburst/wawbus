import requests_mock

from wawbus.api import ZtmApi, ZtmApiException


def test_bus_positions_ok():
    with requests_mock.Mocker() as m:
        api = ZtmApi('test_key')
        m.get(
            'https://api.um.warszawa.pl/api/action/busestrams_get',
            json={'result': [
                {'Lines': '123', 'Lat': 52.0, 'Lon': 21.0,
                 'VehicleNumber': '1234',
                 'Brigade': '1', 'Time': '2021-01-01 12:00:00'},
                {'Lines': '123', 'Lat': 52.1, 'Lon': 21.1,
                 'VehicleNumber': '1235',
                 'Brigade': '1', 'Time': '2021-01-01 12:00:01'}
            ]}
        )
        for entry in api.get_bus_positions():
            assert isinstance(entry, dict)
            assert entry['Lines'] == '123'
            assert entry['Lat'] in (52.0, 52.1)
            assert entry['Lon'] in (21.0, 21.1)
            assert entry['VehicleNumber'] in ('1234', '1235')
            assert entry['Brigade'] == '1'
            assert entry['Time'] in ('2021-01-01 12:00:00',
                                     '2021-01-01 12:00:01')


def test_bus_positions_retry():
    with requests_mock.Mocker() as m:
        api = ZtmApi('test_key', retry_count=3)
        m.get(
            'https://api.um.warszawa.pl/api/action/busestrams_get',
            [{'json': {'result': 'error'}, 'status_code': 200}] +
            [{'json': {'result': []}, 'status_code': 200}] +
            [{'json': {'result': [{'Lines': '123', 'Lat': 52.0, 'Lon': 21.0,
                                   'VehicleNumber': '1234',
                                   'Brigade': '1',
                                   'Time': '2021-01-01 12:00:00'}]},
              'status_code': 200}]
        )
        entry = api.get_bus_positions()[0]
        assert isinstance(entry, dict)
        assert entry['Lines'] == '123'
        assert entry['Lat'] == 52.0
        assert entry['Lon'] == 21.0
        assert entry['VehicleNumber'] == '1234'
        assert entry['Brigade'] == '1'
        assert entry['Time'] == '2021-01-01 12:00:00'


def test_bus_positions_error():
    with requests_mock.Mocker() as m:
        api = ZtmApi('test_key', retry_count=1)
        m.get(
            'https://api.um.warszawa.pl/api/action/busestrams_get',
            json={'json': {'result': 'error'}, 'status_code': 200}
        )
        try:
            api.get_bus_positions()
        except Exception as e:
            assert isinstance(e, ZtmApiException)
        else:
            assert False
