# AWS Deployment Guide

## Recommended Architecture

Use Amazon RDS MySQL as the database layer instead of a self-managed MySQL EC2 server. RDS provides automated backups, patching, Multi-AZ failover, encryption, monitoring, and easier operational recovery. A dedicated database EC2 instance is useful for learning Linux administration, but it is weaker for production reliability and security.

## Network Layout

- Public subnet: frontend EC2 only. It serves static HTML, Bootstrap, and JavaScript through Nginx.
- Private application subnet: backend EC2, internal Network Load Balancer, and API Gateway VPC Link.
- Private database subnet group: RDS MySQL.
- VPC interface endpoint: execute-api endpoint for Private API Gateway access.
- Gateway endpoint: S3 endpoint so backend traffic to S3 stays on the AWS network.

## Request Flow

Browser -> Frontend EC2 Nginx -> Private API Gateway endpoint -> VPC Link -> Internal NLB -> Backend EC2 Nginx -> Gunicorn -> Flask -> RDS metadata and S3 objects.

The backend EC2 security group should not allow public inbound traffic. It should accept HTTP only from the internal NLB security group. RDS should accept MySQL only from the backend EC2 security group.

## API Gateway

1. Create a REST API with endpoint type `Private`.
2. Create an interface VPC endpoint for `com.amazonaws.REGION.execute-api`.
3. Attach a resource policy that only allows calls from that VPC endpoint.
4. Create an internal NLB targeting the backend EC2 instance on port 80.
5. Create an API Gateway VPC Link to the internal NLB.
6. Import `docs/aws/api-gateway-openapi.yaml`.
7. Replace placeholders for API ID, VPC endpoint ID, VPC Link ID, region, and NLB DNS name.
8. Deploy the API to the `api` stage so the base URL becomes `/api/v1`.

## IAM Roles

Attach an IAM role to the backend EC2 instance. Do not create or store AWS access keys on the server.

The backend role needs:

- `secretsmanager:GetSecretValue` for the database secret.
- `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` for the notes bucket prefix.
- CloudWatch Logs permissions for application and container logs.

The frontend EC2 instance does not need S3 or database permissions.

## Secrets Manager

Create a secret named `prod/notes/db` with this shape:

```json
{
  "DB_HOST": "your-rds-endpoint",
  "DB_PORT": "3306",
  "DB_NAME": "notes_db",
  "DB_USER": "notes_user",
  "DB_PASSWORD": "replace-with-generated-password",
  "DB_SSL": "true"
}
```

Pass only `DB_SECRET_ID=prod/notes/db` to the backend container. The password is retrieved at runtime over TLS and is never committed to GitHub.

## Security Groups

Frontend EC2:

- Inbound: 80/443 from approved client CIDRs.
- Outbound: HTTPS to API Gateway VPC endpoint.

Backend EC2:

- Inbound: 80 from internal NLB only.
- Outbound: 3306 to RDS, HTTPS to S3 endpoint and Secrets Manager.

RDS MySQL:

- Inbound: 3306 from backend EC2 security group only.
- Public access: disabled.

## Docker Deployment on EC2

Build and run the frontend container on the frontend server:

```bash
docker build -t notes-frontend ./frontend
docker run -d --name notes-frontend --restart unless-stopped -p 80:80 notes-frontend
```

Build and run the backend container on the backend server:

```bash
docker build -t notes-backend ./backend
docker run -d --name notes-backend --restart unless-stopped \
  -p 80:80 \
  -e AWS_REGION=ap-south-1 \
  -e S3_BUCKET_NAME=your-bucket \
  -e DB_SECRET_ID=prod/notes/db \
  -e DB_SSL=true \
  -e ALLOWED_ORIGINS=https://your-frontend-domain \
  notes-backend
```

## CloudWatch

Install and configure the CloudWatch Agent on both EC2 instances. Ship:

- Docker container stdout and stderr.
- Nginx access and error logs.
- System metrics such as CPU, memory, disk, and network.

Create alarms for:

- Backend 5xx responses.
- API Gateway 4xx/5xx spikes.
- RDS CPU, free storage, and connection count.
- S3 bucket size growth.
