import requests
from flask import Flask, Response, request, jsonify

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource

otlp_exporter = OTLPSpanExporter()
resource = Resource.create({"service.name": "python-proxy"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route('/proxy', methods=["GET"])
def proxy_handler():
    with tracer.start_as_current_span("proxy_handler"):
        r = requests.get("http://127.0.0.1:8080/service")  # call local service
        resp = Response(r.content, r.status_code)
        if "X-Request-Parameter" in r.headers:
            # add contexct to headers
            resp.headers["X-Request-Parameter"] = r.headers["X-Request-Parameter"]
        return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
