# Failure Mode Test Plan

This document describes future manual tests for classifying network failures.

Milestone 1 only creates the plan. Do not run disruptive tests until the monitoring stack is ready.

## Goals

- Confirm that probes detect real failures.
- Confirm that outage classification is understandable.
- Confirm that local alerts work when cloud alerts cannot.
- Build portfolio evidence with screenshots and notes.

## Test Cases

### Raspberry Pi Online, Internet Healthy

Expected result:

- Router is reachable.
- DNS is reachable.
- Internet endpoint is reachable.
- Status is healthy.

### Router or Deco Unreachable

Possible test:

- Disconnect Raspberry Pi from Wi-Fi or Ethernet.
- Turn off Deco only if it is safe to do so.

Expected result:

- Router probe fails.
- Internet probes fail.
- Classifier reports local network or router issue.

### DNS Failure

Possible test:

- Temporarily configure an invalid DNS server in a controlled way.

Expected result:

- IP-based internet checks may work.
- DNS-name checks fail.
- Classifier reports likely DNS issue.

### ACT Internet Outage

Possible test:

- Disconnect the WAN cable from the Deco if safe and reversible.

Expected result:

- Router remains reachable.
- Internet endpoint fails.
- DNS may fail depending on configuration.
- Classifier reports likely ISP or WAN outage.
- Cloud alerts do not send until recovery unless backup internet exists.

### Partial Connectivity

Possible test:

- Compare multiple public targets.

Expected result:

- Some targets fail and others work.
- Classifier reports partial or unknown failure instead of overclaiming.

## Evidence to Capture

For portfolio documentation, capture:

- Grafana dashboard screenshots.
- Alert event examples.
- Classifier output examples.
- Short notes about what was tested and what was learned.

Put future images in the `screenshots/` folder.

