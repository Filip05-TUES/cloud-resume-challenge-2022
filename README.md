# My Cloud Resume Challenge Implementation

**Based on:** Forrest Brazeal — Cloud Resume Challenge (2022)\
**Owner:** Filip Ermenkov\
**Purpose:** Production-focused implementation: static resume (S3 + CloudFront) with a serverless visitor counter (API Gateway → Lambda → DynamoDB) and automated CI/CD via GitHub Actions + OIDC.

---

## Table of contents

1. [At-a-glance summary](#at-a-glance-summary)
2. [Architecture (diagram + explanation)](#architecture-diagram--explanation)
3. [Repository map](#repository-map)
4. [Core CloudFormation templates](#core-cloudformation-templates)
5. [CI/CD & authentication model](#cicd--authentication-model)
6. [Testing strategy & run instructions](#testing-strategy--run-instructions)
7. [Security highlights](#security-highlights)
8. [Observability & alerting](#observability--alerting)
9. [Operational runbook: deploy, rollback, debug](#operational-runbook-deploy-rollback-debug)
10. [Troubleshooting quick commands](#troubleshooting-quick-commands)
11. [Costs For Current Setup](#costs-for-current-setup)
12. [Contacts & license](#contacts--license)

---

## At-a-glance summary

* **Frontend:** S3 (`crc-frontend-bucket`) + CloudFront (OAC) + ACM TLS + Route53 + DNSSEC (KMS-backed KSK).
  S3 is private, versioned, SSE-encrypted, and ownership-enforced.
* **Backend:** API Gateway (regional) exposing `/visitor` → Lambda (Python 3.12) → DynamoDB (`VisitorCounterDB`, PAY_PER_REQUEST, SSE).
* **CI/CD:** GitHub Actions with OIDC assume-role per workflow.
  Unit tests run pre-deploy; Cypress E2E runs post-deploy.
  Lambda artifacts are timestamped and stored in `crc-backend-lambda-code-bucket`.
* **Security & Ops:** WAFv2 (rate-based + AWS managed rules), CloudWatch alarms → SNS → Slack Lambda, IAM Access Analyzer, `cfn-policy-validator` in CI.

---

## Architecture (diagram + explanation)

![Architecture Diagram](https://github.com/user-attachments/assets/dbfb226d-f166-4e9b-bc86-bbf02556103e)

**Flow:**
Users access the resume via CloudFront, which retrieves static assets from S3. The frontend calls an API Gateway endpoint to get and increment a visitor counter. API Gateway invokes a Lambda function, which updates a DynamoDB table. WAF protects the API layer. CloudWatch dashboards and alarms monitor system performance. GitHub Actions deploy both infrastructure and application code using OIDC roles.

---

## Repository map

* `infrastructure/organization/organization.yml` — OUs + AWS accounts (org-formation).
* `infrastructure/identity-center/identity-center.yml` — Identity Center permission sets and assignments.
* `infrastructure/resources/frontend.yml` — S3, CloudFront (OAC), ACM, Route53, DNSSEC KMS.
* `infrastructure/resources/backend.yml` — DynamoDB, Lambda, API Gateway, WAF, CloudWatch, SNS.
* `infrastructure/resources/lambda-bootstrap.yml` — Artifact bucket with versioning, encryption, lifecycle.
* `.github/workflows/` — CI/CD workflows for organization, identity-center, backend, frontend, website sync.
* `src/lambda-functions/` — Lambda function code and unit tests.
* `src/website/` — Static frontend for the resume.
* `cypress/e2e/` — Cypress end-to-end tests.

---

## Core CloudFormation templates

### `identity-center.yml`

Creates Identity Center permission sets and user assignments for production/test accounts.
Uses a fixed Identity Center instance ARN; assignments map a principal to one or more accounts.

### `organization.yml`

Bootstraps the AWS Organization: OUs and member accounts via org-formation (`OC::ORG::*`).
Validated and applied via GitHub Actions workflow.

### `frontend.yml`

Defines the complete static site stack:

* Private S3 bucket (versioned, encrypted, ownership-enforced).
* CloudFront distribution using OAC.
* ACM certificate validated via DNS.
* Route53 alias records.
* DNSSEC using a KMS-backed KSK.

### `backend.yml`

Defines the full backend:

* DynamoDB: PAY_PER_REQUEST, SSE.
* Lambda(s): visitor counter, Slack notifier.
* API Gateway: `/visitor` (GET, POST, OPTIONS).
* WAF WebACL with rate limits + managed rule groups.
* CloudWatch dashboard + alarms.
* SNS topic + Slack webhook Lambda for alerts.

Lambdas reference S3 artifacts via the parameters:
`LambdaCodeS3Bucket`, `VisitorCounterLambdaS3Key`, `SlackWebhookLambdaS3Key`.

### `lambda-bootstrap.yml`

Creates the S3 artifact bucket with versioning, encryption, and lifecycle rules.

---

## CI/CD & authentication model

* **OIDC roles:**
  GitHub Actions assume AWS IAM roles using OIDC and short-lived credentials. No long-lived access keys stored anywhere.

* **Workflow design:**
  Each workflow is path-filtered (org infra, identity, backend, frontend, website). Only relevant parts deploy.

* **Deployment flow (backend):**

  1. Run unit tests.
  2. Package Lambda(s) into timestamped zips.
  3. Upload artifacts to S3.
  4. Deploy CloudFormation with S3 key parameters.
  5. Run E2E tests (Cypress).

* **Policy validation:**
  `cfn-policy-validator` and CFN template validation are invoked before deployment.

---

## Testing strategy & run instructions

### Unit tests (Python)

Located under `src/lambda-functions/test`.

```bash
cd src/lambda-functions
export PYTHONPATH=./code:$PYTHONPATH
python -m unittest discover -v test
```

### Cypress E2E tests

Two specs:

* `api.cy.js` — API behavior
* `resume.cy.js` — UI behavior (count display, increment logic)

Run locally:

```bash
npm ci
npx cypress run --spec "cypress/e2e/*.cy.js" \
  --env apiUrl=https://<api-url>/prod/visitor,baseUrl=https://best-resume-ever.com
```

---

## Security highlights

* **S3:** Block Public Access, BucketOwnerEnforced, SSE (AES256/KMS).
* **CloudFront:** OAC restricts access to S3; ACM certificate with minimum `TLSv1.2_2021`.
* **API Gateway:** CORS restricted to `https://best-resume-ever.com`.
* **WAF:** Rate-based rule (500 req/5 min per IP) + AWS managed rule groups.
* **IAM:** Principle of least privilege for Lambdas and CI roles; Access Analyzer configured.
* **IaC checks:** `cfn-policy-validator` + template validation in CI.

---

## Observability & alerting

* **Dashboard metrics:** Lambda errors, invocations, API p90 latency, WAF blocked requests, estimated billing.
* **CloudWatch alarms:**

  * Lambda errors > 0
  * API p90 latency > 800 ms
  * Invocation spikes
  * High WAF block counts
  * Billing alarm at $50
* **Alerts:**
  SNS → Email + `SlackWebhookLambda`.

---

## Operational runbook: deploy, rollback, debug

### CI deployment

1. Push to `main`.
2. Corresponding workflow runs based on path changes.
3. Infrastructure and/or Lambda code deployed automatically.
4. Cypress runs after successful deployment.

### Manual deployment examples

**Frontend:**

```bash
aws cloudformation deploy \
  --template-file infrastructure/resources/frontend.yml \
  --stack-name frontend-resources \
  --capabilities CAPABILITY_NAMED_IAM
```

**Backend:**

```bash
aws cloudformation deploy \
  --template-file infrastructure/resources/backend.yml \
  --stack-name backend-resources \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    LambdaCodeS3Bucket="crc-backend-lambda-code-bucket" \
    VisitorCounterLambdaS3Key="visitor_counter_code_20250101120000.zip" \
    SlackWebhookLambdaS3Key="slack_webhook_code_20250101120000.zip"
```

### Rollback strategy

* CloudFormation rolls back automatically on failure.
* For full rollback, redeploy a known-good tagged release or previously deployed S3 artifact version.

### Quick debug checklist

1. Inspect CloudFormation events.
2. Check Lambda logs for stack traces.
3. Review WAF logs for blocked requests.
4. Verify CORS configuration and API endpoint correctness.
5. Ensure CloudFront cache is invalidated if frontend behavior is inconsistent.

---

## Troubleshooting quick commands

**Find CFN failures:**

```bash
aws cloudformation describe-stack-events --stack-name <stack-name> \
  --query "StackEvents[?ResourceStatus=='CREATE_FAILED' || ResourceStatus=='ROLLBACK_IN_PROGRESS'].[LogicalResourceId,ResourceStatus,ResourceStatusReason]" \
  --output table
```

**Lambda logs:**

```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/VisitorCounterLambda \
  --limit 50
```

**Find CloudFront distribution for a domain:**

```bash
aws cloudfront list-distributions \
  --query "DistributionList.Items[?contains(Aliases.Items,'best-resume-ever.com')].[Id,DomainName]" \
  --output table
```

**Access Analyzer:**

```bash
aws accessanalyzer list-findings --analyzer-name UnusedAccessAnalyzer
```

---

## Costs for current setup

* **DynamoDB:** Very low for small traffic; scales linearly.
* **API Gateway:** Per-request charges.
* **CloudFront:** CDN costs depend on egress volume.
* **WAF:** WebACL + managed rules incur additional monthly cost.

**Total Costs Per Month:** 25$

---

## Contacts & license

**Owner:** Filip Ermenkov — [f.ermenkov@gmail.com](mailto:f.ermenkov@gmail.com)\
**License:** This project is licensed under the [MIT License](LICENSE).