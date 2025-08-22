from flask import Flask, jsonify, make_response
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource

otlp_exporter = OTLPSpanExporter()
resource = Resource.create({"service.name": "python-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route('/service', methods=["GET"])
def service_handler():
    request_parameter = "test123"  # ← pretend this comes from deserialization
    with tracer.start_as_current_span("service_handler") as span:
        span.set_attribute("request_parameter", request_parameter)
        response = make_response(jsonify({
            "message": "Hello from service!",
            "request_parameter": request_parameter,
        }))
        # propagate up
        response.headers["X-Request-Parameter"] = request_parameter
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
