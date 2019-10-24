"""Application metrics for Synse Server."""

import time

import sanic
from prometheus_client import Counter, Histogram, core
from prometheus_client.exposition import CONTENT_TYPE_LATEST, generate_latest
from sanic.response import raw


class Monitor:

    _req_start_time = '__req_start_time'

    # Counter for the total number of requests received by Sanic.
    http_req_count = Counter(
        name='sanic_http_request_count',
        documentation='Sanic HTTP Request Count',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    http_req_latency = Histogram(
        name='sanic_http_request_latency_sec',
        documentation='Sanic HTTP Request Latency',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    http_resp_bytes = Counter(
        name='sanic_http_response_bytes',
        documentation='Sanic HTTP Response Bytes',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    def __init__(self, app: sanic.Sanic) -> None:
        self.app = app

    def register(self) -> None:
        """Register the metrics monitor with the Sanic application.

        This adds the metrics endpoint as well as setting up various metrics
        collectors.
        """

        @self.app.middleware('request')
        async def before_request(request):
            request[self._req_start_time] = time.time()

        @self.app.middleware('response')
        async def before_response(request, response):
            latency = time.time() - request[self._req_start_time]

            # WebSocket handler ignores response logic, so default
            # to a 200 response in such case.
            code = response.status if response else 200
            labels = (request.method, request.path, code)

            self.http_req_latency.labels(*labels).observe(latency)
            self.http_req_count.labels(*labels).inc()

            # We cannot use Content-Length header since that has not yet been
            # calculated and added to the response headers.
            if response.body is not None:
                self.http_resp_bytes.labels(*labels).inc(len(response.body))

        @self.app.route('/metrics', methods=['GET'])
        async def metrics(_):
            return raw(
                generate_latest(core.REGISTRY),
                content_type=CONTENT_TYPE_LATEST,
            )
