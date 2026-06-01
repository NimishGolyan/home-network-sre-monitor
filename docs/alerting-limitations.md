# Alerting Limitations

This project monitors a home network, so alerting has an important limitation:

If ACT internet is down, the Raspberry Pi may not be able to send cloud alerts.

That means email, webhooks, mobile push, or chat alerts may fail during the exact outage you want to detect.

## Local-First Alerting

The first reliable alert path should be local.

Examples:

- Raspberry Pi buzzer.
- Raspberry Pi LED.
- Local Grafana dashboard.
- Optional Google Home announcement if local network communication still works.

These can work even when the internet is unavailable, depending on what part of the network failed.

## Delayed Cloud Alerts

Cloud alerts can still be useful after recovery.

Example flow:

1. ACT outage starts.
2. Raspberry Pi detects loss of internet.
3. Local buzzer or LED alerts immediately.
4. Raspberry Pi stores the outage event locally.
5. Internet recovers.
6. Raspberry Pi sends a delayed cloud alert or summary.

## Backup Internet

Cloud alerts during an ACT outage require backup internet, such as:

- Mobile hotspot.
- Secondary ISP.
- LTE modem.

Without backup internet, cloud alerts should be treated as best-effort only.

## Portfolio Note

This limitation is not a weakness. It is a realistic SRE design constraint. Good monitoring documents what cannot work and explains the fallback behavior.

