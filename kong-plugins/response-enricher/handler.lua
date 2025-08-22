local ResponseEnricherHandler = {
  PRIORITY = 1000,
  VERSION = "0.1.0",
}

function ResponseEnricherHandler:header_filter(conf)
  local span = kong.tracing.active_span()
  if not span then return end

  local req_param = kong.response.get_header("X-Request-Parameter")
  if req_param then
    span:set_attribute("request_parameter", req_param)
    kong.log.debug("Root span enriched with request_parameter=" .. req_param)
  end
end

return ResponseEnricherHandler
