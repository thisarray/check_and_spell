"""Compounding interest calculator.

It uses the daily balance method which applies a daily periodic rate."""

import datetime
import math
import unittest

DAYS_IN_YEAR = 365
"""Integer number of days in a year."""

def _get_daily_rate_from_apy(apy):
    """Return the daily interest rate that compounds to apy in 365 days.

    Args:
        apy: Float annual percentage yield as a decimal not a percentage.
    Returns:
        Float daily interest rate that compounds to apy in 365 days.
    """
    return math.pow(1.0 + apy, 1.0 / float(DAYS_IN_YEAR)) - 1.0

def _get_maturity(today, day_count = 0, month_count = 0, year_count = 0):
    """Return a datetime.date object as specified in the future from today.

    Args:
        day_count: Integer number of days to add to today.
        month_count: Integer number of months to add to today.
        year_count: Integer number of years to add to today.
    Returns:
        datetime.date object as specified in the future from today.
    """
    if not isinstance(today, datetime.date):
        raise TypeError('today must be a datetime.date.')
    if not isinstance(day_count, int):
        raise TypeError('day_count must be a non-negative int.')
    if not isinstance(month_count, int):
        raise TypeError('month_count must be a non-negative int.')
    if not isinstance(year_count, int):
        raise TypeError('year_count must be a non-negative int.')
    if day_count < 0:
        raise ValueError('day_count must be a non-negative int.')
    if month_count < 0:
        raise ValueError('month_count must be a non-negative int.')
    if year_count < 0:
        raise ValueError('year_count must be a non-negative int.')

    result = datetime.date(today.year, today.month, today.day)
    extra_years, month_count = divmod(month_count, 12)
    year_count += extra_years

    # At this point, 0 <= month_count < 12
    end_month = result.month + month_count
    if end_month > 12:
        year_count += 1
        end_month -= 12

    # Decrement the end day until we find a valid day
    end_day = result.day
    while True:
        try:
            result = datetime.date(
                result.year + year_count, end_month, end_day)
        except ValueError:
            day_count += 1
            end_day -= 1
        else:
            # result is a valid date so break the loop
            break

    if day_count > 0:
        # Increment result by the leftover number of days
        result = datetime.date.fromordinal(result.toordinal() + day_count)

    return result

def compound(principal, apy, today, maturity):
    """Return the result of principal compounded at apy from today to maturity.

    Interest is compounded daily and rounded to the nearest cent.

    Args:
        principal: Integer or float amount of the principal.
        apy: Float annual percentage yield as a decimal not a percentage.
        today: datetime.date to today's date.
        maturity: datetime.date to the date of maturity
            greater than or equal to today.
    Returns:
        Float amount at the end of compounding.
    """
    if not isinstance(today, datetime.date):
        raise TypeError('today must be a datetime.date.')
    if not isinstance(maturity, datetime.date):
        raise TypeError('maturity must be a datetime.date >= today.')
    if maturity < today:
        raise ValueError('maturity must be a datetime.date >= today.')

    rate = _get_daily_rate_from_apy(apy)
    result = float(principal)
    for i in range(maturity.toordinal() - today.toordinal()):
        result += round(result * rate, 2)
    return result


class _UnitTest(unittest.TestCase):
    def test_get_daily_rate_from_apy(self):
        """Test calculating the daily interest rate from the APY."""
        for value in [None, '', []]:
            self.assertRaises(TypeError, _get_daily_rate_from_apy, value)
        for value in [0.01, 0.015, 0.0175, 0.02, 0.0225, 0.025, 0.0275, 0.03]:
            rate = _get_daily_rate_from_apy(value)
            self.assertAlmostEqual(math.pow(1.0 + rate, DAYS_IN_YEAR),
                                   1.0 + value)

    def test_get_maturity(self):
        """Test calculating the maturity in days, months, and years."""
        today = datetime.date(2021, 2, 3)
        for value in [None, 42.0, '', []]:
            self.assertRaises(TypeError, _get_maturity, value)
            self.assertRaises(TypeError, _get_maturity, today, value)
            self.assertRaises(TypeError, _get_maturity, today, 0, value)
            self.assertRaises(TypeError, _get_maturity, today, 0, 0, value)
            self.assertRaises(TypeError, _get_maturity, today,
                              day_count=value)
            self.assertRaises(TypeError, _get_maturity, today,
                              month_count=value)
            self.assertRaises(TypeError, _get_maturity, today,
                              year_count=value)
        for value in [-1]:
            self.assertRaises(ValueError, _get_maturity, today, value)
            self.assertRaises(ValueError, _get_maturity, today, 0, value)
            self.assertRaises(ValueError, _get_maturity, today, 0, 0, value)
            self.assertRaises(ValueError, _get_maturity, today,
                              day_count=value)
            self.assertRaises(ValueError, _get_maturity, today,
                              month_count=value)
            self.assertRaises(ValueError, _get_maturity, today,
                              year_count=value)

        self.assertEqual(today, _get_maturity(today))
        self.assertEqual(today, _get_maturity(today, 0))
        self.assertEqual(today, _get_maturity(today, 0, 0))
        self.assertEqual(today, _get_maturity(today, 0, 0, 0))
        self.assertEqual(today, _get_maturity(today, day_count=0))
        self.assertEqual(today, _get_maturity(today, month_count=0))
        self.assertEqual(today, _get_maturity(today, year_count=0))
        self.assertEqual(_get_maturity(today, DAYS_IN_YEAR),
                         _get_maturity(today, month_count=12))
        self.assertEqual(_get_maturity(today, DAYS_IN_YEAR),
                         _get_maturity(today, year_count=1))
        self.assertEqual(_get_maturity(today, month_count=12),
                         _get_maturity(today, year_count=1))
        self.assertEqual(_get_maturity(today, DAYS_IN_YEAR * 2),
                         _get_maturity(today, month_count=24))
        self.assertEqual(_get_maturity(today, DAYS_IN_YEAR * 2),
                         _get_maturity(today, year_count=2))
        self.assertEqual(_get_maturity(today, month_count=24),
                         _get_maturity(today, year_count=2))
        self.assertEqual(_get_maturity(today, DAYS_IN_YEAR * 3),
                         _get_maturity(today, month_count=36))
        self.assertEqual(_get_maturity(today, DAYS_IN_YEAR * 3),
                         _get_maturity(today, year_count=3))
        self.assertEqual(_get_maturity(today, month_count=36),
                         _get_maturity(today, year_count=3))

        for value in range(DAYS_IN_YEAR * 3):
            self.assertEqual(
                _get_maturity(today, value).toordinal() - today.toordinal(),
                value)
        for value in range(61):
            year_delta, month_delta = divmod(value, 12)
            end_month = today.month + month_delta
            if end_month > 12:
                year_delta += 1
                end_month -= 12
            expected = datetime.date(
                today.year + year_delta, end_month, today.day)
            for date in [_get_maturity(today, 0, value),
                         _get_maturity(today, month_count=value)]:
                self.assertEqual(date, expected)
        for value in range(10):
            expected = datetime.date(
                today.year + value, today.month, today.day)
            for date in [_get_maturity(today, 0, 0, value),
                         _get_maturity(today, year_count=value)]:
                self.assertEqual(date, expected)

    def test_get_maturity_month(self):
        """Test adjusting for different number of days in a month."""
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 28), 0, 1),
                         datetime.date(2020, 2, 28))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 29), 0, 1),
                         datetime.date(2020, 2, 29))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 30), 0, 1),
                         datetime.date(2020, 3, 1))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 31), 0, 1),
                         datetime.date(2020, 3, 2))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 28), 0, 2),
                         datetime.date(2020, 3, 28))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 29), 0, 2),
                         datetime.date(2020, 3, 29))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 30), 0, 2),
                         datetime.date(2020, 3, 30))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 31), 0, 2),
                         datetime.date(2020, 3, 31))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 28), 0, 3),
                         datetime.date(2020, 4, 28))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 29), 0, 3),
                         datetime.date(2020, 4, 29))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 30), 0, 3),
                         datetime.date(2020, 4, 30))
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 31), 0, 3),
                         datetime.date(2020, 5, 1))

        for i in range(3):
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 28), 0, 1 + (12 * i)),
                datetime.date(2021 + i, 2, 28))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 29), 0, 1 + (12 * i)),
                datetime.date(2021 + i, 3, 1))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 30), 0, 1 + (12 * i)),
                datetime.date(2021 + i, 3, 2))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 31), 0, 1 + (12 * i)),
                datetime.date(2021 + i, 3, 3))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 28), 0, 2 + (12 * i)),
                datetime.date(2021 + i, 3, 28))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 29), 0, 2 + (12 * i)),
                datetime.date(2021 + i, 3, 29))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 30), 0, 2 + (12 * i)),
                datetime.date(2021 + i, 3, 30))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 31), 0, 2 + (12 * i)),
                datetime.date(2021 + i, 3, 31))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 28), 0, 3 + (12 * i)),
                datetime.date(2021 + i, 4, 28))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 29), 0, 3 + (12 * i)),
                datetime.date(2021 + i, 4, 29))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 30), 0, 3 + (12 * i)),
                datetime.date(2021 + i, 4, 30))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 31), 0, 3 + (12 * i)),
                datetime.date(2021 + i, 5, 1))
            self.assertEqual(
                _get_maturity(datetime.date(2021, 1, 28), 0, 12 + (12 * i)),
                datetime.date(2022 + i, 1, 28))

    def test_get_maturity_leap_day(self):
        """Test calculating the maturity for a Leap Day."""
        leap_day = datetime.date(2020, 2, 29)
        self.assertEqual(_get_maturity(datetime.date(2020, 2, 28), 1),
                         leap_day)
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 29), 0, 1),
                         leap_day)
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 29),
                                       month_count=1), leap_day)
        self.assertEqual(_get_maturity(datetime.date(2020, 1, 28), 1, 1),
                         leap_day)
        for value in range(1, 8):
            self.assertEqual(_get_maturity(datetime.date(2020, 2, 29 - value),
                                           value), leap_day)
            self.assertEqual(_get_maturity(leap_day, value),
                             datetime.date(2020, 3, value))
            self.assertEqual(_get_maturity(leap_day, month_count=value),
                             datetime.date(2020, 2 + value, 29))
            if value == 4:
                self.assertEqual(_get_maturity(leap_day, year_count=value),
                                 datetime.date(2020 + value, 2, 29))
            else:
                self.assertEqual(_get_maturity(leap_day, year_count=value),
                                 datetime.date(2020 + value, 3, 1))

    def test_compound(self):
        """Test compounding using an annual percentage yield."""
        today = datetime.date(2021, 2, 3)
        tomorrow = datetime.date(2021, 2, 4)
        self.assertRaises(TypeError, compound, None, 0.2, today, today)
        self.assertRaises(ValueError, compound, '', 0.2, today, today)
        self.assertRaises(TypeError, compound, [], 0.2, today, today)
        for value in [None, 42, '', []]:
            self.assertRaises(TypeError, compound, 1000, 0.2, value, today)
            self.assertRaises(TypeError, compound, 1000, 0.2, today, value)
        self.assertRaises(ValueError, compound, 1000, 0.2, tomorrow, today)

        expected = 1000.0
        for value in [0, 0.0, 0.01, 0.015, 0.0175, 0.02, 0.0225, 0.025, 0.0275,
                      0.03]:
            self.assertEqual(compound(expected, value, today, today), expected)
            self.assertAlmostEqual(
                compound(expected, value, today, tomorrow),
                expected + (expected * _get_daily_rate_from_apy(value)),
                places=2)

        maturity = datetime.date(today.year + 1, today.month, today.day)
        for value in [1000, 1000.0]:
            self.assertAlmostEqual(compound(value, 0.02, today, maturity),
                                   1019.15)
            self.assertAlmostEqual(compound(value, 0.2, today, maturity),
                                   1199.99)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-d', '--day', type=int, default=0,
        help='integer number of days to compound')
    parser.add_argument(
        '-m', '--month', type=int, default=0,
        help='integer number of months to compound')
    parser.add_argument(
        '-y', '--year', type=int, default=0,
        help='integer number of years to compound')
    parser.add_argument(
        'principal', type=float, default=0,
        help='amount of the principal')
    parser.add_argument(
        'apy', type=float, default=0,
        help='annual percentage yield')
    args = parser.parse_args()

    if (args.principal > 0) and (args.apy > 0):
        today = datetime.date.today()
        maturity = _get_maturity(today, args.day, args.month, args.year)
        if args.apy > 0.25:
            # apy is generally not more than 25%
            # so it must have been specified as a percentage if it is greater
            apy = args.apy / 100.0
        else:
            apy = args.apy
        result = compound(args.principal, apy, today, maturity)
        print('${:.2f} @ {:.2%} APY = ${:.2f} on {} \
(${:.2f} in interest)'.format(
    args.principal, apy, result, maturity.isoformat(),
    result - args.principal))
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(_UnitTest)
        unittest.TextTestRunner(verbosity=2).run(suite)
