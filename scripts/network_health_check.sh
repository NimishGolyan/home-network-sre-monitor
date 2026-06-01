#!/usr/bin/env sh

# Placeholder network health check for home-network-sre-monitor.
# This script is intentionally simple for Milestone 1.

set -eu

ROUTER_IP="${ROUTER_IP:-192.168.68.1}"
PRIMARY_DNS="${PRIMARY_DNS:-1.1.1.1}"

echo "Network health check placeholder"
echo "Router IP placeholder: ${ROUTER_IP}"
echo "Primary DNS placeholder: ${PRIMARY_DNS}"

# TODO: Add a router reachability check.
# TODO: Add a DNS reachability check.
# TODO: Add a DNS resolution check.
# TODO: Add an internet reachability check.
# TODO: Return machine-readable output for the outage classifier.

