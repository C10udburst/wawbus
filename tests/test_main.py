import requests_mock

from wawbus import WawBus


def _wraprow(*row):
    return {"result": row}


def _mkrow(lat, lon, time, vehicle):
    return ({
        "Lat": lat,
        "Lon": lon,
        "Time": time,
        "VehicleNumber": vehicle,
        "Brigade": "1",
        "Lines": "123"
    })


def test_collect_positions():
    row1 = _mkrow(52.2296133, 21.0123688, '2021-01-01 12:00:00', '1234')
    with requests_mock.Mocker() as m:
        m.get(
            'https://api.um.warszawa.pl/api/action/busestrams_get',
            [
                {'json': {"result": "test error"}},  # this should be ignored
                {'json': _wraprow(row1), 'status_code': 200},
                {'json': {"result": "test error"}},  # this should be ignored
                {'json': {"result": "test error"}},  # this should be ignored
                {'json': _wraprow(row1), 'status_code': 200},
                {'json': {"result": "test error"}},  # this should be ignored
            ]
        )
        wb = WawBus(apikey='test_key')
        wb.collect_positions(2, 0)
        assert len(wb.dataset) == 2
        assert wb.dataset['Lat'].values[0] == 52.2296133
        assert wb.dataset['Lon'].values[0] == 21.0123688
        assert wb.dataset['Lat'].values[1] == 52.2296133
        assert wb.dataset['Lon'].values[1] == 21.0123688
        assert wb.dataset['VehicleNumber'].values[0] == '1234'
        assert wb.dataset['VehicleNumber'].values[1] == '1234'
        assert wb.dataset['Brigade'].values[0] == '1'
        assert wb.dataset['Brigade'].values[1] == '1'
        assert wb.dataset['Lines'].values[0] == '123'
        assert wb.dataset['Lines'].values[1] == '123'
        assert len(wb.dataset.columns) == 6
        assert "|".join(wb.dataset.columns) == "Lat|Lon|Time|Lines|VehicleNumber|Brigade"


def test_speed():
    epsilon = 0.05

    row1 = _mkrow(52.2296133, 21.0123688, '2021-01-01 12:00:00', '1234')
    row2 = _mkrow(52.2323437, 21.009987, '2021-01-01 12:00:30', '1234')
    with requests_mock.Mocker() as m:
        m.get(
            'https://api.um.warszawa.pl/api/action/busestrams_get',
            [
                {'json': _wraprow(row1), 'status_code': 200},
                {'json': {"result": "test error"}},  # this should be ignored
                {'json': _wraprow(row2), 'status_code': 200}
            ]
        )
        wb = WawBus(apikey='test_key')
        wb.collect_positions(2, 0)
        df = wb.calculate_speed()
        assert len(df) == 2
        df = df.dropna()
        assert len(df) == 1
        assert abs(df['Speed'].values[0] - 41.31) < epsilon


def test_speed_2buses():
    epsilon = 0.05

    with requests_mock.Mocker() as m:
        m.get(
            'https://api.um.warszawa.pl/api/action/busestrams_get',
            [
                {'json': _wraprow(
                    _mkrow(52.2296133, 21.0123688, '2021-01-01 12:00:00', '1234'),
                    _mkrow(52.2323437, 21.009987, '2021-01-01 12:00:01', '1235')
                ), 'status_code': 200},
                {'json': {"result": "test error"}},  # this should be ignored
                {'json': {"result": "test error"}},  # this should be ignored
                {'json': _wraprow(
                    _mkrow(52.2323437, 21.009987, '2021-01-01 12:00:30', '1234'),
                    _mkrow(52.2296133, 21.0123688, '2021-01-01 12:00:29', '1235')
                ), 'status_code': 200},
                {'json': {"result": "test error"}},  # this should be ignored
                {'json': {"result": "test error"}},  # this should be ignored
            ]
        )

        wb = WawBus(apikey='test_key')
        wb.collect_positions(2, 0)
        df = wb.calculate_speed()
        df = df.dropna()
        assert len(df) == 2

        assert abs(df['Speed'].values[0] - 41.31) < epsilon
        assert abs(df['Speed'].values[1] - 44.3) < epsilon
