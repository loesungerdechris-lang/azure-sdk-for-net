FROM golang:1.23.10-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY cmd ./cmd
COPY internal ./internal
RUN go test ./... && go build -trimpath -ldflags="-s -w" -o /out/sentinel-monitor ./cmd/sentinel-monitor

FROM alpine:3.20
RUN addgroup -S sentinel && adduser -S -D -H -u 10001 -G sentinel sentinel \
    && mkdir -p /tmp/sentinel \
    && chown -R 10001:10001 /tmp/sentinel
WORKDIR /app
COPY --from=build /out/sentinel-monitor /app/sentinel-monitor
USER 10001:10001
ENV HEALTH_PATH=/tmp/sentinel/health.json
ENV SELF_TEST_INTERVAL=60s
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["/app/sentinel-monitor", "healthcheck"]
ENTRYPOINT ["/app/sentinel-monitor"]
