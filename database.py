#! /usr/bin/env python

"""
Tasks are the main objects we read, display, and modify
"""

import datetime
import fcntl
import json
import os
import re
import timestamp
import yaml


class Database:
    """Task objects and methods"""

    def __init__(self):
        self.datadir = os.environ.get('NOWPLAYING_DATADIR')
        if self.datadir is None:
            raise RuntimeError("NOWPLAYING_DATADIR not set in env")
        self.dbdir = os.path.join(self.datadir, "DB")


    def append_to_db(self, timestamp, json_text):
        year_part, month_part, date_part = self.timestamp_to_logpath_parts(timestamp)
        year_path  = os.path.join(self.dbdir, year_part)
        month_path = os.path.join(year_path, month_part)
        date_path  = os.path.join(month_path, date_part)
        if not os.path.exists(year_path):
            os.mkdir(year_path)
        if not os.path.exists(month_path):
            os.mkdir(month_path)
        with open(date_path, "a") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            fh.write(f"{timestamp}: {json_text}\n")
            #time.sleep(0.1)
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            fh.close()

    def insert(self, json_text):
        ts = timestamp.Timestamp()
        entry = json.loads(json_text)
        stamp = self.pad_timestamp(entry['timestamp'])
        entry['timestamp'] = stamp
        entry['meta']['inserted'] = self.pad_timestamp(ts.now_timestamp())
        self.append_to_db(stamp, json.dumps(entry))

    def update(self, id, json_text):
        ts = timestamp.Timestamp()
        entry = json.loads(self.fetch_by_id(id))
        new_vals = json.loads(json_text)
        entry.update(new_vals)
        entry['meta']['updated'] = self.pad_timestamp(ts.now_timestamp())
        self.append_to_db(id, json.dumps(entry))

    def fetch_by_id(self, id):
        out = None
        id = self.pad_timestamp(id)
        filename = self.timestamp_to_fullpath(id)
        with open(filename, "r") as fh:
            for line in fh:
                entry = line.split(': ', 1)
                if entry[0] == id:
                    out = entry[1]
        return(out)


    def files_in_range(self, start, end):
        top_dir = self.dbdir
        out = []
        for year_dir in os.listdir(top_dir):
            if not re.match(r"^\d{10,11}-\d{10,11}-\d{4}$", year_dir):
                break
            y_min, y_max, desc = year_dir.split('-',2)
            if ((start <= y_max) and (end >= y_min)):
                month_dirs = os.path.join(top_dir, year_dir)
                for month_dir in os.listdir(month_dirs):
                    if not re.match(r"^\d{10,11}-\d{10,11}-\d{4}:\d{2}$", month_dir):
                        break
                    m_min, m_max, desc = month_dir.split('-',2)
                    if start <= m_max and end >= m_min:
                        dates_dir = os.path.join(month_dirs, month_dir)
                        for date_file in os.listdir(dates_dir):
                            if not re.match(r"^\d{10,11}-\d{10,11}-\d{4}:\d{2}:\d{2}$", date_file):
                                break
                            d_min, d_max, desc = date_file.split('-',2)
                            if start <= d_max and end >= d_min:
                                out.append(os.path.join(dates_dir, date_file))
        return(out) # unsorted

    def entries_in_range(self, min_stamp, max_stamp, type):
        out = {}
        files = self.files_in_range(min_stamp, max_stamp)
        for file in files:
            with open(file, "r") as fh:
                for line in fh:
                    stamp, entry = line.split(': ', 1)
                    if stamp >= min_stamp and stamp <= max_stamp:
                        if (type == 'ANY'):
                            out[stamp] = entry.rstrip()
                        else:
                            data = json.loads(entry)
                            if data['type'] == type:
                                out[stamp] = entry.rstrip()
        return(out)







    def pad_timestamp(self, timestamp):
        st = timestamp.split('.')
        return(f"{st[0]}.{st[1]:{0}<7}")



    def timestamp_to_logpath_parts(self, stamp):
        ts = timestamp.Timestamp()
        dt = datetime.datetime.fromtimestamp(float(stamp), tz=datetime.timezone.utc)
        ys, ye = ts.timestamp_range_of_utc_year(dt.year)
        ms, me = ts.timestamp_range_of_utc_month(dt.year, dt.month)
        ds, de = ts.timestamp_range_of_utc_date(dt.year, dt.month, dt.day)
        #hs, he = self.timestamp_range_of_utc_hour(dt.year, dt.month, dt.day, dt.hour)
        return([
            f"{ys}-{ye}-{dt.year}",
            f"{ms}-{me}-{dt.year}:{dt.month:>0{2}}",
            f"{ds}-{de}-{dt.year}:{dt.month:>0{2}}:{dt.day:>0{2}}",
        ])

    def timestamp_to_fullpath(self, timestamp):
        year_part, month_part, date_part = self.timestamp_to_logpath_parts(timestamp)
        year_path  = os.path.join(self.dbdir, year_part)
        month_path = os.path.join(year_path, month_part)
        date_path  = os.path.join(month_path, date_part)
        return(date_path)



######################################


def main() -> None:
    """Entry point"""
    db = Database()
    ts = timestamp.Timestamp()
    now = ts.now_timestamp()
    stamp = str(float(now) - 123)

    entry = {}
    entry['timestamp'] = stamp
    entry['type'] = 'TEST'
    entry['meta'] = {}

    json_text = json.dumps(entry)
    print (f"ENTRY: {json_text}")
    db.insert(json_text)
    print (f"FETCH: 1764795886.2370830")
    print(db.fetch_by_id('1764795886.2370830'))
    #db.update('1764795886.2370830', '{"DJ": "Tom", "Loc": "MCR"}')
    #print(db.fetch_by_id('1764795886.2370830'))
    print(f"NOW: {now}")
    print(db.files_in_range(str(float(now) - 86123), str(float(now) + 123)))
    print("---")
    print(db.entries_in_range(str(1764795402),str(1764795884), 'TEST'))
    print(yaml.dump(db.entries_in_range(str(1764795800),str(1764796000), 'ANY')))



if __name__ == "__main__":
    main()
