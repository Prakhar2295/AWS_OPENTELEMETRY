import os
from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import metrics

app = Flask(__name__)

# Set up OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Read the OTLP endpoint from the environment variable
otlp_endpoint = os.getenv('OTLP_ENDPOINT', 'http://localhost:4317')

# Configure the OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

# Create a BatchSpanProcessor and add it to the tracer provider
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask with OpenTelemetry
FlaskInstrumentor().instrument_app(app)

hello_world_counter = meter.create_counter(
    name="hello_world_requests",
    description="Counts the number of requests to the /hello endpoint",
    unit="1"
)


@app.route('/hello')
def hello_world():
    with tracer.start_as_current_span("hello_world_span"):
        span = trace.get_current_span()
        span.set_attribute("custom.log", "INFO")
        span.set_attribute("custom.log", "HELLO")
        
        hello_world_counter.add(1)
        
        return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True,port=5000)
