# Cloud Heartbeat Alerting

This design adds external loss-of-contact alerting without pretending that cloud heartbeat alone is root cause analysis.

## Goal

If ACT internet goes down and the Raspberry Pi cannot send Telegram/email directly, AWS can still notice that the Pi stopped checking in.

This is a dead-man heartbeat:

```text
Raspberry Pi -> AWS heartbeat endpoint -> stale checker -> email alert
```

## Important Design Principle

Cloud heartbeat means:

```text
The home monitor is no longer reaching AWS.
```

It does not automatically mean:

```text
ACT is definitely down.
```

Possible causes include:

- ACT outage.
- Deco/router outage.
- Raspberry Pi power loss.
- Raspberry Pi process failure.
- Home power outage.
- AWS credential/config issue.

The local classifier provides better root-cause evidence when the Pi is online or after it recovers.

## AWS Components

The CloudFormation template in `infra/aws/cloud-heartbeat.yml` creates:

- API Gateway HTTP endpoint for heartbeats.
- Lambda function to receive heartbeats.
- DynamoDB table to store latest heartbeat state.
- EventBridge rule that checks heartbeat freshness every minute.
- Lambda function that sends stale/recovery notifications.
- SNS topic with email subscription.

Default region for India:

```text
ap-south-1
```

## Raspberry Pi Components

The Raspberry Pi runs:

```sh
python3 scripts/send_heartbeat.py
```

The script:

- Runs `scripts/classify_outage.py`.
- Sends the JSON summary to AWS.
- Queues failed sends under `logs/heartbeat_queue.jsonl`.
- Flushes queued payloads after connectivity returns.

## Alert Confidence

Recommended wording:

```text
LOW confidence:
Cloud heartbeat missing. Home monitor unreachable from AWS.

HIGH confidence:
Pi later reports gateway was up while public internet was down.
Classification: ACT_OUTAGE.
```

## Deployment

Authenticate AWS CLI first.

```sh
aws sts get-caller-identity
```

Deploy the stack:

```sh
aws cloudformation deploy \
  --region ap-south-1 \
  --stack-name home-network-sre-heartbeat \
  --template-file infra/aws/cloud-heartbeat.yml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    AlertEmail=you@example.com \
    HeartbeatToken=replace-with-a-long-random-secret \
    SiteId=home \
    StaleAfterSeconds=180
```

After deployment, confirm the SNS subscription email AWS sends you.

Get the heartbeat URL:

```sh
aws cloudformation describe-stacks \
  --region ap-south-1 \
  --stack-name home-network-sre-heartbeat \
  --query "Stacks[0].Outputs"
```

## Raspberry Pi Configuration

Set environment variables on the Raspberry Pi:

```sh
export HEARTBEAT_URL="https://example.execute-api.ap-south-1.amazonaws.com/prod/heartbeat"
export HEARTBEAT_TOKEN="replace-with-the-same-long-random-secret"
export HEARTBEAT_SITE_ID="home"
```

Send one heartbeat:

```sh
python3 scripts/send_heartbeat.py
```

## Scheduling

For the first test, run manually.

Later, use cron or a systemd timer to run every minute:

```text
* * * * * cd /home/nimish/home-network-sre-monitor && HEARTBEAT_URL="..." HEARTBEAT_TOKEN="..." python3 scripts/send_heartbeat.py >> logs/heartbeat.log 2>&1
```

Do not commit real heartbeat URLs or tokens.

## Cost Notes

At home-project scale, this should usually be very low cost:

- Lambda invocations are tiny.
- DynamoDB on-demand usage is tiny.
- EventBridge runs once per minute.
- SNS email is inexpensive.
- No EC2 instance is required.

SMS is intentionally not part of this design.

## Pros

- Alerts when you are away from home.
- Does not depend on the Pi sending an alert during outage.
- Cheap serverless architecture.
- Good SRE story: local detection plus external loss-of-contact monitoring.

## Cons

- Missing heartbeat is not root cause by itself.
- Needs AWS account and email subscription confirmation.
- Requires false-positive controls such as stale thresholds and deduplication.
- If home power fails, Pi cannot collect local classification until it recovers.

