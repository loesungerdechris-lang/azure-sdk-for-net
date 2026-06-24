FROM golang:1.22-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY cmd ./cmd
COPY internal ./internal
RUN go test ./... && go build -trimpath -ldflags="-s -w" -o /out/sentinel-monitor ./cmd/sentinel-monitor

FROM alpine:3.20
RUN adduser -D -H -u 10001 sentinel
WORKDIR /app
COPY --from=build /out/sentinel-monitor /app/sentinel-monitor
USER 10001:10001
ENV HEALTH_PATH=/tmp/sentinel-health.json
ENTRYPOINT ["/app/sentinel-monitor"]
