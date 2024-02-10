def timeint(x):
    """
    Pandas UDF which returns seconds from 00:00:00.

    Args:
        x: Timestamp

    Returns:
        int: Seconds from 00:00:00
    """
    return x.hour * 3600 + x.minute * 60 + x.second
