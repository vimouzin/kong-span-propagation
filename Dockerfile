# Start from the official Kong 3.7 image
FROM kong:3.7

# Create the directory for our custom plugin
RUN mkdir -p /usr/local/share/lua/5.1/kong/plugins/response-enricher

# Copy the plugin source code into the image
COPY ./kong-plugins/response-enricher /usr/local/share/lua/5.1/kong/plugins/response-enricher

# Set the environment variables directly in the image.
# This ensures all necessary plugins are always loaded.
ENV KONG_PLUGINS="bundled,opentelemetry,response-enricher"
ENV KONG_TRACING_INSTRUMENTATIONS="all"
ENV KONG_TRACING_SAMPLING_RATE="1.0"