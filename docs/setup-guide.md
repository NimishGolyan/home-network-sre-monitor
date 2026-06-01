# Setup Guide

This guide is intentionally beginner-friendly. Milestone 1 does not require running the full stack yet.

## Prerequisites

Eventually you will need:

- Raspberry Pi connected to your home network.
- Docker installed on the Raspberry Pi.
- Docker Compose available.
- Git installed.

For Milestone 1, you only need this repository.

## Configuration

1. Review `.env.example`.
2. Copy it to `.env` when you are ready to configure local values.
3. Replace placeholder values with your actual local settings.

Do not commit `.env`.

## Router IP

The current Windows CLI check detected:

- Active adapter: Wi-Fi
- Local IPv4 address: `192.168.68.100`
- Local subnet: `192.168.68.0/24`
- TP-Link Deco gateway: `192.168.68.1`
- DHCP server: `192.168.68.1`
- IPv4 DNS servers: `1.1.1.2`, `1.0.0.2`
- DNS over HTTPS endpoint: `https://security.cloudflare-dns.com/dns-query`

These are private/local network details and Cloudflare DNS details. Do not commit public IP addresses or secrets.

The examples use `192.168.68.1` as the TP-Link Deco gateway IP. Your real Deco gateway may be different if the network is reconfigured.

You can usually find it from:

- The Deco app.
- Your computer network settings.
- A command such as `ip route` on Linux.

On Windows, useful commands are:

```powershell
ipconfig /all
Get-NetIPConfiguration
Get-DnsClientServerAddress -AddressFamily IPv4
Get-NetRoute -AddressFamily IPv4
Get-DnsClientDohServerAddress
```

## First Docker Command

In a later milestone, the expected command will be:

```sh
docker compose up -d
```

For now, the Compose file is only a placeholder so you can review the project shape.

## Beginner Notes

- Prometheus stores measurements over time.
- Blackbox Exporter tests whether targets are reachable.
- Grafana turns metrics into dashboards.
- Alerts should include local options because cloud notifications may fail during an ISP outage.
