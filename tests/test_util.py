from wawbus.util.dist import haversine


def test_haversine():
    epsilon = 0.05
    assert abs(haversine(21.1816406, 50.0077390, 19.8632813, 52.6097194) - 303.5) < epsilon
    assert abs(haversine(21.1816406, 50.0077390, 21.1816406, 50.0077390) - 0) < epsilon
    assert abs(haversine(19.3798828, 52.6097194, 176.4843750, 63.1543552) - 6989.0) < epsilon
