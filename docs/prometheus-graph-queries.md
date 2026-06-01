# Prometheus Graph Queries

Use these queries in Prometheus at `http://192.168.68.109:9090/graph` or in Grafana panels.

## Service Health

Shows whether each scrape target is up.

```promql
up
```

Shows only the monitoring host.

```promql
up{instance="raspberry-pi",host="raspberry-pi"}
```

## Network Probe Health

Shows whether each Blackbox probe is succeeding.

```promql
probe_success
```

Deco gateway reachability.

```promql
probe_success{instance="deco-gateway"}
```

External HTTPS reachability.

```promql
probe_success{instance="google-https"}
```

DNS lookup checks.

```promql
probe_success{target_type="dns-lookup"}
```

## Probe Latency

Shows probe duration in seconds.

```promql
probe_duration_seconds
```

Deco gateway latency.

```promql
probe_duration_seconds{instance="deco-gateway"}
```

External HTTPS latency.

```promql
probe_duration_seconds{instance="google-https"}
```

## Raspberry Pi Load

One-minute system load.

```promql
node_load1{instance="raspberry-pi",host="raspberry-pi"}
```

Five-minute system load.

```promql
node_load5{instance="raspberry-pi",host="raspberry-pi"}
```

Fifteen-minute system load.

```promql
node_load15{instance="raspberry-pi",host="raspberry-pi"}
```

## Raspberry Pi Memory

Available memory in bytes.

```promql
node_memory_MemAvailable_bytes{instance="raspberry-pi",host="raspberry-pi"}
```

Memory usage percentage.

```promql
100 * (1 - (node_memory_MemAvailable_bytes{instance="raspberry-pi",host="raspberry-pi"} / node_memory_MemTotal_bytes{instance="raspberry-pi",host="raspberry-pi"}))
```

## Raspberry Pi Disk

Root filesystem usage percentage.

```promql
100 - ((node_filesystem_avail_bytes{instance="raspberry-pi",host="raspberry-pi",mountpoint="/",fstype!~"tmpfs|overlay"} * 100) / node_filesystem_size_bytes{instance="raspberry-pi",host="raspberry-pi",mountpoint="/",fstype!~"tmpfs|overlay"})
```

Root filesystem available bytes.

```promql
node_filesystem_avail_bytes{instance="raspberry-pi",host="raspberry-pi",mountpoint="/",fstype!~"tmpfs|overlay"}
```

## Raspberry Pi Network

Network receive rate by interface.

```promql
rate(node_network_receive_bytes_total{instance="raspberry-pi",host="raspberry-pi",device!="lo"}[5m])
```

Network transmit rate by interface.

```promql
rate(node_network_transmit_bytes_total{instance="raspberry-pi",host="raspberry-pi",device!="lo"}[5m])
```
