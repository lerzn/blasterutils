from datetime import timedelta, datetime
from dateutil import parser


def daterange(start_date, end_date):
    """
    Accepts either datetime objects or str in format YYYY-MM-DD for start_date and end_date.
    Works similar to built-in range(). Source: https://stackoverflow.com/a/1060330/9268478

    Usage:

    >>> for single_date in daterange('2018-12-01', '2018-12-05'):
    >>>     print(single_date)
    2018-12-01 00:00:00
    2018-12-02 00:00:00
    2018-12-03 00:00:00
    2018-12-04 00:00:00

    :param start_date:
    :param end_date:
    :return: generator
    """
    if not isinstance(start_date, datetime):
        start_date = parser.parse(start_date)
    if not isinstance(end_date, datetime):
        end_date = parser.parse(end_date)
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
