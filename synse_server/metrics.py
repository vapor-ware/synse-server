"""Application metrics for Synse Server."""

import time

import grpc
import sanic
from prometheus_client import Counter, Gauge, Histogram, core
from prometheus_client.exposition import CONTENT_TYPE_LATEST, generate_latest
from sanic.request import Request
from sanic.response import HTTPResponse, raw


class Monitor:

    #
    # Metrics for Synse Server's HTTP API
    #
    http_req_count = Counter(
        name='synse_http_request_count',
        documentation='The total number of HTTP requests processed',
        labelnames=('method', 'template', 'endpoint', 'http_code', 'ip'),
    )

    http_req_latency = Histogram(
        name='synse_http_request_latency_sec',
        documentation='The time it takes for an HTTP request to be fulfilled',
        labelnames=('method', 'template', 'endpoint', 'http_code', 'ip'),
    )

    http_resp_bytes = Counter(
        name='synse_http_response_bytes',
        documentation='The total number of bytes returned in HTTP API responses',
        labelnames=('method', 'template', 'endpoint', 'http_code', 'ip'),
    )

    #
    # Metrics for Synse Server's WebSocket API
    #
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

    #
    # Metrics for Synse Server's internal gRPC API
    #
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

    grpc_req_latency = Histogram(
        name='synse_grpc_request_latency_sec',
        documentation='The time it takes for a gRPC request to be fulfilled',
        labelnames=('type', 'service', 'method', 'plugin'),
    )

    #
    # Metrics around Synse Server's plugin state/status
    #
    plugin_active = Gauge(
        name='synse_plugin_active_state',
        documentation='Whether a plugin is currently in the active (1) or inactive (0) state',
        labelnames=('plugin',),
    )

    plugin_connects = Counter(
        name='synse_plugin_connect_count',
        documentation='The total number of times a plugin has been successfully connected to',
        labelnames=('plugin',),
    )

    plugin_disconnects = Counter(
        name='synse_plugin_disconnect_count',
        documentation='The total number of times a plugin has disconnected (become unreachable)',
        labelnames=('plugin',),
    )

    plugin_disabled = Gauge(
        name='synse_plugin_disabled',
        documentation='The number of plugins which are currently in a "disabled" state',
        labelnames=('plugin',),
    )

    def __init__(self, app: sanic.Sanic) -> None:
        self.app = app

    def register(self) -> None:
        """Register the metrics monitor with the Sanic application.

        This adds the metrics endpoint as well as setting up various metrics
        collectors.
        """

        @self.app.middleware('request')
        async def before_request(request: Request) -> None:
            request.ctx.req_start_time = time.time()

        @self.app.middleware('response')
        async def before_response(request: Request, response: HTTPResponse) -> None:
            # If there is no request start time captured in the request context, we cannot
            # measure request latency, so do not use it.
            #
            # This case is indicative of a 404 or some bad request coming in and the request
            # immediately resolving to an error response via the Sanic framework.
            if hasattr(request.ctx, 'req_start_time'):
                latency = time.time() - request.ctx.req_start_time
            else:
                latency = None

            # WebSocket handler ignores response logic, so default
            # to a 200 response in such case.
            code = response.status if response else 200
            labels = (request.method, request.uri_template, request.path, code, request.ip)

            if request.path != '/metrics':
                if latency is not None:
                    self.http_req_latency.labels(*labels).observe(latency)
                self.http_req_count.labels(*labels).inc()

                # We cannot use Content-Length header since that has not yet been
                # calculated and added to the response headers.
                #
                # Streaming responses do not have a 'body' attribute, so we cannot
                # collect this data in those cases.
                if hasattr(response, 'body') and response.body is not None:
                    self.http_resp_bytes.labels(*labels).inc(len(response.body))

        @self.app.route('/metrics', methods=['GET'])
        async def metrics(_) -> HTTPResponse:
            return raw(
                generate_latest(core.REGISTRY),
                content_type=CONTENT_TYPE_LATEST,
            )


class MetricsInterceptor(grpc.UnaryUnaryClientInterceptor,
                         grpc.UnaryStreamClientInterceptor):

    type_unary = "unary"
    type_server_stream = "server_streaming"

    def __init__(self):
        # Initialize with no plugin defined. This is because we create the
        # gRPC client before we know the identity of the plugin.
        self.plugin = ''

    def intercept_unary_unary(self, continuation, client_call_details, request):
        service, method = get_metadata(client_call_details)

        Monitor.grpc_msg_sent.labels(
            self.type_unary,
            service, method,
            self.plugin,
        ).inc()

        start = time.time()
        resp = continuation(client_call_details, request)

        Monitor.grpc_req_latency.labels(
            self.type_unary,
            service,
            method,
            self.plugin,
        ).observe(time.time() - start)

        Monitor.grpc_msg_received.labels(
            self.type_unary,
            service,
            method,
            self.plugin,
        ).inc()

        return resp

    def intercept_unary_stream(self, continuation, client_call_details, request):
        service, method = get_metadata(client_call_details)

        Monitor.grpc_msg_sent.labels(
            self.type_server_stream,
            service, method,
            self.plugin,
        ).inc()

        start = time.time()
        resp = continuation(client_call_details, request)

        Monitor.grpc_req_latency.labels(
            self.type_server_stream,
            service,
            method,
            self.plugin,
        ).observe(time.time() - start)

        return wrap_stream_resp(
            response=resp,
            counter=Monitor.grpc_msg_received,
            grpc_type=self.type_server_stream,
            service=service,
            method=method,
            plugin=self.plugin,
        )


def get_metadata(call_details):
    """Get metadata gets the service name and method name from the client
    call details.

    The method should be structured like "/{service}/{method}". This function
    will split apart the components and return them individually.
    """

    items = call_details.method.split('/')
    if len(items) < 3:
        return '', ''

    return items[1:3]


def wrap_stream_resp(response, counter, grpc_type, service, method, plugin):
    """Wrap a stream response so the individual returned messages can be counted."""

    for item in response:
        counter.labels(
            grpc_type,
            service,
            method,
            plugin,
        ).inc()
        yield item
