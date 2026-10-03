FROM golang:1.27.1-alpine3.24@sha256:8a5910f31396cd4d89662f56c68b3ae31d374308270a1c3bd96672ee5ed43414 AS build
WORKDIR /src
COPY go.mod ./
COPY cmd ./cmd
COPY internal ./internal
RUN go test ./... && CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/sentinel-monitor ./cmd/sentinel-monitor

FROM alpine:3.24.2@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6
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
