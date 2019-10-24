"""Application metrics for Synse Server."""

import sanic
from prometheus_client import CONTENT_TYPE_LATEST, core, Counter, Histogram
from prometheus_client.exposition import generate_latest
from sanic.response import raw
import time


class Monitor:

    _req_start_time = '__req_start_time'

    # Counter for the total number of requests received by Sanic.
    req_count = Counter(
        name='sanic_request_count',
        documentation='Sanic Request Count',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    req_latency = Histogram(
        name='sanic_request_latency_sec',
        documentation='Sanic Request Latency',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    def __init__(self, app: sanic.Sanic) -> None:
        self.app = app

    def register(self) -> None:
        """Register the metrics monitor with the Sanic application.

        This adds the metrics endpoint as well as setting up various metrics
        collectors.
        """

        # @self.app.listener('before_server_start')
        # def before_server(app, loop):
        #     pass

        @self.app.middleware('request')
        async def before_request(request):
            request[self._req_start_time] = time.time()

        @self.app.middleware('response')
        async def before_response(request, response):
            latency = time.time() - request[self._req_start_time]

            # WebSocket handler ignores response logic, so default
            # to a 200 response in such case.
            code = response.status if response else 200

            self.req_latency.labels(request.method, request.path, code).observe(latency)
            self.req_count.labels(request.method, request.path, code).inc()

        @self.app.route('/metrics', methods=['GET'])
        async def metrics(request):
            return raw(
                generate_latest(core.REGISTRY),
                content_type=CONTENT_TYPE_LATEST,
            )
