# -*- coding: utf-8 -*-
import base64
import os
import pickle
import socket
import requests
import urllib

from dateutil import rrule
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from lib.logger import Logger

logger = Logger('Helper')

def is_numeric(value):
    try:
        return isinstance(int(value), int)
    except ValueError:
        return False

def save_cookie(data):
    return pickle.dumps(data)

def load_cookie(data):
    return pickle.loads(data)

def current_process_id():
    return os.getpid()

def get_host_name():
    return socket.gethostname()

def get_as_base64(url):
    try:
        img = base64.b64encode(requests.get(url).content)
    except:
        raise
    return img

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def date_range(start, stop, step_days=1):
    result = []
    current = start
    step = timedelta(step_days)
    if step_days > 0:
        while current <= stop:
            result.append(current)
            current += step
    elif step_days < 0:
        while current >= stop:
            result.append(current)
            current += step
    else:
        raise ValueError("date_range() step_days argument must not be zero")
    return result

def get_date_range(start_date, end_date):
    result = []
    try:
        start_date = datetime.strptime(start_date, '%Y%m%d')
        end_date = datetime.strptime(end_date, '%Y%m%d')
        ranges = end_date - start_date
        for i in range(ranges.days + 1):
            raw_date = datetime.strftime((start_date + timedelta(days=i)).date(), '%Y-%m-%d')
            result.append(raw_date)
    except Exception:
        raise
    return result

def get_month_range(Yeatstart, Monthstart, Yearend, Monthend):
    result = []
    try:
        start = datetime(Yeatstart, Monthstart, 1)
        end = datetime(Yearend, Monthend, 1)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=start, until=end):
            Datestart = dt.date()
            next_month = Datestart.replace(day=28) + timedelta(days=4)
            Dateend = next_month - timedelta(days=next_month.day)
            temp = {'Datestart': Datestart.strftime('%Y%m%d'), 'Dateend': Dateend.strftime('%Y%m%d')}
            result.append(temp)
    except Exception:
        raise
    return result

def extract_url_params(url):
    parse = urlsplit(url)
    url = "{}://{}{}".format(parse.scheme, parse.netloc, parse.path)
    parameter = dict(urllib.parse.parse_qsl(parse.query))
    return {"url": url, "query": parameter}
