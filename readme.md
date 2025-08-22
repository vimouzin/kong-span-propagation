# Propagating request_parameter to Gateway Spans for Trace Filtering

This project shows how to propagate a custom request_parameter from a service up to the top-level gateway span in a Kong-based API flow. The service adds the parameter to its span and includes it in the response header. A Kong Lua plugin (ResponseEnricherHandler) reads this header and attaches the value to the gateway’s active span, ensuring the top-level span contains the same contextual information as the service span.

By enriching the gateway span, you can filter and group traces in Dash0 based on this parameter.


## Components

### Backend (`service.py`)
- Simple Flask service handling requests at `/service`.
- Adds a `request_parameter` to its OpenTelemetry span.
- Optionally sends the `X-Request-Parameter` header back to the proxy.

### Proxy (`proxy.py`)
- Flask service sitting between the client and the backend.
- Receives client requests at `/proxy`.
- Forwards requests to the backend and returns the response to the client.
- Propagates the `X-Request-Parameter` header back to the client.
- Creates its own OpenTelemetry span for tracing the proxy request.

### Gateway (`Handler.lua`,`ResponseEnricherHandler` Lua plugin)
- Kong plugin that runs in the `header_filter` phase after the response is received.
- Retrieves the gateway's active span using `kong.tracing.active_span()`.
- Reads the `X-Request-Parameter` header from the response.
- Adds `request_parameter` as an attribute to the gateway span.
- Enables filtering and grouping of traces at the top-most gateway level in Dash0.
##




## How to Run
pip3 install -r requirements
python3 service.py
python3 proxy.py

docker build -t kong-custom .

docker run -d \          
 --name kong-gateway \
 --network=kong-net \
 -e "KONG_DATABASE=off" \
 -e "KONG_DECLARATIVE_CONFIG=/usr/local/kong/declarative/kong.yaml" \
 -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
 -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
 -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
 -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
 -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
 -v "$(pwd)/kong.yaml:/usr/local/kong/declarative/kong.yaml" \
 -p 8000:8000 \
 -p 8001:8001 \
 kong-custom


 curl localhost:8000/proxy