#! /usr/bin/env python

"""
Tasks are the main objects we read, display, and modify
"""

#from datetime import datetime, timezone
import calendar
import datetime
from dateutil.parser import parse
from dateutil import tz
#import functools
import os
from time import time
import subprocess
from typing import Any, Dict, Union
from zoneinfo import ZoneInfo

class Timestamp:
    """Task objects and methods"""

    def __init__(self):
        self.timezone = os.environ.get('TZ')
        if self.timezone is None:
            raise RuntimeError("TZ (timezone) not set in env")
        #self.utc_tzinfo = ZoneInfo("UTC")
        self.local_tzinfo = ZoneInfo("us/eastern")

    ###
    # get now

    def now_timestamp(self):
        return(str(time()))

    ###
    # transmorging

    def iso_to_timestamp(self, string):
        obj=parse(string, fuzzy=True)
        return(obj.strftime('%s.%f'))

    def timestamp_to_utciso(self,timestamp):
        format = "%Y-%m-%dT%H:%M:%S.%f%z"
        return(datetime.datetime.fromtimestamp(float(timestamp), tz=datetime.timezone.utc).strftime(format))

    def timestamp_to_localiso(self, timestamp):
        format = "%Y-%m-%dT%H:%M:%S.%f%z"
        utc_obj = datetime.datetime.fromtimestamp(float(timestamp), tz=datetime.timezone.utc)
        local_obj = utc_obj.replace(tzinfo=tz.UTC).astimezone(self.local_tzinfo)
        return(local_obj.strftime(format))

    def utcarray_to_timestamp(self, y, m, d, H, M, S):
        dt = datetime.datetime(y, m, d, H, M, S, 0, tzinfo=datetime.timezone.utc)
        return(dt.timestamp())

    def localarray_to_timestamp(self, y, m, d, H, M, S):
        dt = datetime.datetime(y, m, d, H, M, S, 0, tzinfo=self.local_tzinfo)
        return(dt.timestamp())

    ###
    # range for time periods

    def timestamp_range_of_utc_year(self, y):
        return([
            self._timestamp_beginning_of_utc_year(y),
            self._timestamp_end_of_utc_year(y)
        ])

    def timestamp_range_of_utc_month(self, y, m):
        return([
            self._timestamp_beginning_of_utc_month(y, m),
            self._timestamp_end_of_utc_month(y, m)
        ])

    def timestamp_range_of_utc_date(self, y, m, d):
        return([
            self._timestamp_beginning_of_utc_date(y, m, d),
            self._timestamp_end_of_utc_date(y, m, d)
        ])

    def timestamp_range_of_utc_hour(self, y, m, d, h):
        return([
            self._timestamp_beginning_of_utc_hour(y, m, d, h),
            self._timestamp_end_of_utc_hour(y, m, d, h)
        ])


    ###########################################################################
    # Private

    def _days_in_month(self, y, m):
        return calendar.monthrange(y, m)[1]

    ###
    # Beginning of time periods

    def _timestamp_beginning_of_utc_year(self, y):
        return(str(int(self.utcarray_to_timestamp(y, 1, 1,  0, 0, 0))))

    def _timestamp_beginning_of_utc_month(self, y, m):
        return(str(int(self.utcarray_to_timestamp(y, m, 1,  0, 0, 0))))

    def _timestamp_beginning_of_utc_date(self, y, m, d):
        return(str(int(self.utcarray_to_timestamp(y, m, d,  0, 0, 0))))

    def _timestamp_beginning_of_utc_hour(self, y, m, d, h):
        return(str(int(self.utcarray_to_timestamp(y, m, d,  h, 0, 0))))

    ###
    # End of time periods

    def _timestamp_end_of_utc_year(self, y):
        y = y + 1
        dt = int(self.utcarray_to_timestamp(y, 1, 1,  0, 0, 0))
        return (str(dt))

    def _timestamp_end_of_utc_month(self, y, m):
        m = m + 1
        if (m == 13):
            y = y + 1
            m = 1
        dt = int(self.utcarray_to_timestamp(y, m, 1,  0, 0, 0))
        return (str(dt))

    def _timestamp_end_of_utc_date(self, y, m, d):
        max_d = self._days_in_month(y, m)
        d = d + 1
        if (d > max_d):
            d = 1
            m = m + 1
            if (m == 13):
                m = 1
                y = y + 1
        dt = int(self.utcarray_to_timestamp(y, m, d,  0, 0, 0))
        return (str(dt))

    def _timestamp_end_of_utc_hour(self, y, m, d, h):
        h = h + 1
        if (h == 24):
            h = 1
            d = d + 1
            max_d = self._days_in_month(y, m)
            if (d > max_d):
                d = 1
                m = m + 1
                if (m == 13):
                    m = 1
                    y = y + 1
        dt = int(self.utcarray_to_timestamp(y, m, d,  h, 0, 0))
        return (str(dt))



################################################################################
################################################################################

def main() -> None:
    """Entry point"""
    test_basics()
    test_setting_from_array()
    test_ranges()

def test_basics():
    """Entry point"""
    ts = Timestamp()

    timestamp = ts.now_timestamp();

    print (banner("BASIC TESTS"))
    print (f"+++ {time()}")
    print (timestamp)
    utc_timestring = ts.timestamp_to_utciso(timestamp)
    print ("UTC_ISO: ", utc_timestring)
    ret = ts.iso_to_timestamp(utc_timestring)
    print ("MATCH: ", ret)
    print ("LOCAL: ", ts.timestamp_to_localiso(timestamp))
    print ("-----")
    print ("NOW:")
    stamp = ts.now_timestamp()
    print ("    STAMP: ", stamp)
    print ("    UTC:   ", ts.timestamp_to_utciso(stamp));
    print ("    LOCAL: ", ts.timestamp_to_localiso(stamp));
    print

def test_setting_from_array():
    ts = Timestamp()
    timestamp = ts.now_timestamp();
    print (banner("TEST SETTING TIMESTAMP FROM ARRAY"))
    print ("UTC_ARRAY")
    stamp = ts.utcarray_to_timestamp(2025,12,3,12,15,35)
    print ("    IN:     2025,12,3, 12,15,35 -- UTC")
    print ("    STAMP: ", stamp)
    print ("    UTC:   ", ts.timestamp_to_utciso(stamp), "   (should be 12:15 +0000)");
    print ("    LOCAL: ", ts.timestamp_to_localiso(stamp), "   (should be 07:15 -0500)");
    print ("")
    print ("-----")
    print ("LOCAL_ARRAY")
    stamp = ts.localarray_to_timestamp(2025,12,3,12,15,35)
    print ("    IN:     2025,12,3, 12,15,35 -- LOCAL_TZ")
    print ("    STAMP: ", stamp)
    print ("    UTC:   ", ts.timestamp_to_utciso(stamp), "   (should be 17:15 +0000)");
    print ("    LOCAL: ", ts.timestamp_to_localiso(stamp), "   (should be 12:15 -0500)");

def test_ranges():
    ts = Timestamp()
    timestamp = ts.now_timestamp();
    print (banner("TEST RANGES"))

    print ("    2024:")
    start, end = ts.timestamp_range_of_utc_year(2024)
    show_range(start, end)

    print ("    2025:")
    start, end = ts.timestamp_range_of_utc_year(2025)
    show_range(start, end)

    print ("    2024-02:")
    start, end = ts.timestamp_range_of_utc_month(2024, 2)
    show_range(start, end)

    print ("    2025-02:")
    start, end = ts.timestamp_range_of_utc_month(2025, 2)
    show_range(start, end)

    print ("    2025-06-07")
    start, end = ts.timestamp_range_of_utc_date(2025, 6, 7)
    show_range(start, end)

    print ("    2025-06-07 14:00")
    start, end = ts.timestamp_range_of_utc_hour(2025, 6, 7, 14)
    show_range(start, end)

def banner (string):
    bar = "================================================"
    return(f"\n{bar}\n=== {string}\n{bar}\n")

def show_range(start, end):
    ts = Timestamp()
    dur = int(end) - int(start)
    print (f"      START: {start}   {ts.timestamp_to_utciso(start)}")
    print (f"      END:   {end}   {ts.timestamp_to_utciso(end)}")
    print (f"      DUR:   {dur:> {10}}   {seconds_to_summary(dur)}")

def seconds_to_summary(s):
    d = 0
    h = 0
    m = 0
    if s >= 86400:
        d = int(s / 86400)
        s = s % 86400
    if s >= 3600:
        h = int(s / 3600)
        s = s % 3600
    if s >= 60:
        m = int(s / 60)
        s = s % 60
    return(f"{d} days, {h} hours, {m} minutes, {s} seconds")


if __name__ == "__main__":
    main()
