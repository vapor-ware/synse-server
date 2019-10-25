"""Application metrics for Synse Server."""

import time

import sanic
from prometheus_client import Counter, Histogram, Gauge, core
from prometheus_client.exposition import CONTENT_TYPE_LATEST, generate_latest
from sanic.response import raw


class Monitor:

    _req_start_time = '__req_start_time'

    # Counter for the total number of requests received by Sanic.
    http_req_count = Counter(
        name='synse_http_request_count',
        documentation='The total number of HTTP requests processed',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    http_req_latency = Histogram(
        name='synse_http_request_latency_sec',
        documentation='The time it takes for an HTTP request to be fulfilled',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    http_resp_bytes = Counter(
        name='synse_http_response_bytes',
        documentation='The total number of bytes returned in HTTP API responses',
        labelnames=('method', 'endpoint', 'http_code'),
    )

    ws_req_count = Counter(
        name='synse_websocket_request_count',
        documentation='The total number of WebSocket requests processed',
        labelnames=('event',),
    )

    ws_req_latency = Histogram(
        name='synse_websocket_request_latency_sec',
        documentation='The time it takes for a WebSocket request to be fulfilled',
        labelnames=('event',),
    )

    ws_req_bytes = Counter(
        name='synse_websocket_request_bytes',
        documentation='The total number of bytes received from WebSocket requests',
        labelnames=('event',),
    )

    ws_resp_bytes = Counter(
        name='synse_websocket_response_bytes',
        documentation='The total number of bytes returned from the WebSocket API',
        labelnames=('event',),
    )

    ws_resp_error_count = Counter(
        name='synse_websocket_error_response_count',
        documentation='The total number of error responses returned by the WebSocket API',
        labelnames=('event',)
    )

    ws_session_count = Gauge(
        name='synse_websocket_session_count',
        documentation='The total number of active WebSocket sessions connected to Synse Server',
        labelnames=('source',),
    )

    grpc_msg_sent = Counter(
        name='synse_grpc_message_sent',
        documentation='The total number of gRPC messages sent to plugins',
        labelnames=('type', 'service', 'method', 'plugin'),
    )

    grpc_msg_received = Counter(
        name='synse_grpc_message_received',
        documentation='The total number of gRPC messages received from plugins',
        labelnames=('type', 'service', 'method', 'plugin'),
    )

    grpc_req_latenct = Histogram(
        name='synse_grpc_request_latency_sec',
        documentation='The time it takes for a gRPC request to be fulfilled',
        labelnames=('type', 'service', 'method', 'plugin'),
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
