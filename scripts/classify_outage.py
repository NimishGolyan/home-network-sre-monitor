#!/usr/bin/env python3
"""
Placeholder outage classifier for home-network-sre-monitor.

Future goal:
Compare router, DNS, and internet probe results to classify likely outage type.
"""


def classify_outage():
    """Return a placeholder status until real probe inputs are implemented."""
    # TODO: Read current probe results from Prometheus or a local JSON file.
    # TODO: Detect whether the TP-Link Deco gateway is reachable.
    # TODO: Detect whether DNS resolution works.
    # TODO: Detect whether public internet targets are reachable.
    # TODO: Classify likely states:
    #       - healthy
    #       - raspberry_pi_issue
    #       - local_network_issue
    #       - router_or_deco_issue
    #       - dns_issue
    #       - isp_or_act_outage
    #       - partial_or_unknown_failure
    # TODO: Store outage events locally so cloud alerts can be sent after recovery.
    return "TODO: outage classification not implemented yet"


if __name__ == "__main__":
    print(classify_outage())

