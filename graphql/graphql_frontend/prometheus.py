""" GraphQL Frontend

    Author:  Thomas Rampelberg
    Date:    4/7/2017

    \\//
     \/apor IO
"""

import logging
from datetime import datetime

import prometheus_client
import prometheus_client.exposition
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client.core import _INF
from pytz import utc

import graphql_frontend.schema

query = '''{
    clusters {
        id
        racks {
            id
            boards {
                id
                devices {
                    id
                    info
                    device_type
                    ... on TemperatureDevice {
                        temperature_c
                    }
                    ... on FanSpeedDevice {
                        speed_rpm
                    }
                    ... on PowerDevice {
                        input_power
                    }
                }
            }
        }
    }
}'''

_metrics = {
    "histogram": {},
    "gauge": {}
}


class Device(object):

    default_labels = [
        "cluster_id",
        "rack_id",
        "board_id",
        "device_id",
        "device_info",
        "device_type"
    ]

    _filter_keys = [
        "id",
        "info",
        "device_type"
    ]

    _buckets = {
        "fan_speed": list(range(0, 8500, 500)) + [_INF],
        "temperature": list(range(0, 95, 5)) + [_INF],
        "power": list(range(0, 400, 10)) + [_INF]
    }

    def __init__(self, cluster, rack, board, device):
        self._cluster = cluster
        self._rack = rack
        self._board = board
        self._device = device

    @property
    def type(self):
        return self._device.get("device_type")

    @property
    def labels(self):
        return [
            self._cluster.get("id"),
            self._rack.get("id"),
            self._board.get("id"),
            self._device.get("id"),
            self._device.get("info"),
            self.type
        ]

    def name(self, _type, param):
        return 'device_{0}_{1}_{2}'.format(self.type, _type, param)

    def histogram(self, name):
        return prometheus_client.Histogram(
            name,
            '',
            self.default_labels,
            buckets=self._buckets.get(self.type))

    def gauge(self, name):
        return prometheus_client.Gauge(name, '', self.default_labels)

    def get_metric(self, _type, param):
        name = self.name(_type, param)
        if name not in _metrics.get(_type):
            _metrics.get(_type)[name] = getattr(self, _type)(name)

        return _metrics.get(_type).get(name).labels(*self.labels)

    def record(self):
        for k, v in self._device.items():
            if k in self._filter_keys:
                continue
            try:
                self.get_metric('gauge', k).set(v)
                self.get_metric('histogram', k).observe(v)
            except Exception as ex:
                logging.error("failed to log metric: {0}".format(self.type))


summary = prometheus_client.Summary('device_refresh_seconds', '')


@summary.time()
def get():
    schema = graphql_frontend.schema.create()
    result = schema.execute(query)

    for error in result.errors:
        logging.exception("Query error", exc_info=error)
        if hasattr(error, "message"):
            logging.debug(error.message)

    for cluster in result.data.get("clusters"):
        if not cluster:
            continue
        for rack in cluster.get("racks"):
            if not rack:
                continue
            for board in rack.get("boards"):
                if not board:
                    continue
                for device in board.get("devices"):
                    if not device:
                        continue
                    Device(cluster, rack, board, device).record()


def refresh():
    scheduler = BackgroundScheduler(timezone=utc)
    scheduler.add_job(
        get,
        'interval',
        minutes=5,
        next_run_time=datetime.now(utc))
    scheduler.start()


def metrics():
    return prometheus_client.exposition.generate_latest()
