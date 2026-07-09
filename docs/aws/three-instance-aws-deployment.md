# Three-Instance AWS Deployment

This deployment uses three separate AWS runtime targets:

1. Frontend EC2 instance
2. Backend EC2 instance
3. Amazon RDS MySQL database instance

Amazon RDS is the recommended database instance because it gives automated backups, patching, encryption, monitoring, and easier recovery than a self-managed MySQL EC2 server.

## Target Architecture

```text
User Browser
  -> Frontend EC2: Docker + Nginx + HTML/Bootstrap/JavaScript
  -> API Gateway
  -> Backend EC2: Docker + Nginx + Gunicorn + Flask
  -> RDS MySQL: metadata
  -> S3: uploaded files
```

## Region

Use the same region for all resources:

```text
eu-north-1
```

## Resource Names

```text
S3 bucket: aws-cloud-notes-storage-oobat
Frontend EC2 name: notes-frontend-ec2
Backend EC2 name: notes-backend-ec2
RDS name: notes-mysql-rds
Database name: notes_db
Database user: notes_user
Secrets Manager secret: prod/notes/db
```

## Security Groups

### Frontend Security Group

Name:

```text
notes-frontend-sg
```

Inbound:

```text
HTTP 80 from 0.0.0.0/0
HTTPS 443 from 0.0.0.0/0 optional
SSH 22 from your IP only
```

Outbound:

```text
HTTPS 443 to API Gateway / internet
```

### Backend Security Group

Name:

```text
notes-backend-sg
```

Inbound for first working deployment:

```text
HTTP 80 from frontend security group
SSH 22 from your IP only
```

After API Gateway is configured, restrict HTTP 80 to the internal load balancer or API Gateway VPC Link path.

Outbound:

```text
HTTPS 443 to S3 and Secrets Manager
MySQL 3306 to RDS security group
```

### RDS Security Group

Name:

```text
notes-rds-sg
```

Inbound:

```text
MySQL 3306 from notes-backend-sg only
```

Public access:

```text
Disabled
```

## IAM Role for Backend EC2

Create an IAM role for EC2:

```text
notes-backend-ec2-role
```

Attach a policy that allows:

```text
secretsmanager:GetSecretValue
s3:PutObject
s3:GetObject
s3:DeleteObject
logs:CreateLogGroup
logs:CreateLogStream
logs:PutLogEvents
```

Use the example policy in:

```text
docs/aws/backend-ec2-instance-policy.json
```

## RDS MySQL

Create an RDS MySQL database:

```text
Engine: MySQL
Template: Free tier or Dev/Test
DB identifier: notes-mysql-rds
Database name: notes_db
Username: notes_user
Public access: No
Security group: notes-rds-sg
Storage encryption: Enabled
Backups: Enabled
```

Save the password in Secrets Manager, not in GitHub or Dockerfiles.

## Secrets Manager

Create this secret:

```text
Name: prod/notes/db
```

Secret value:

```json
{
  "DB_HOST": "your-rds-endpoint.eu-north-1.rds.amazonaws.com",
  "DB_PORT": "3306",
  "DB_NAME": "notes_db",
  "DB_USER": "notes_user",
  "DB_PASSWORD": "your-rds-password",
  "DB_SSL": "true"
}
```

## Frontend EC2 Deployment

Install Docker:

```bash
sudo yum update -y
sudo yum install -y docker git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user
```

Clone repository:

```bash
git clone https://github.com/Battleboy-bot/aws-cloud-notes-storage-system-3-layer-architecture.git
cd aws-cloud-notes-storage-system-3-layer-architecture
```

Build and run frontend:

```bash
docker build -t notes-frontend ./frontend
docker run -d --name notes-frontend --restart unless-stopped \
  -p 80:80 \
  -e API_BASE_URL=https://YOUR_API_GATEWAY_URL/api/v1 \
  notes-frontend
```

For the first simple test before API Gateway, temporarily use:

```bash
-e API_BASE_URL=http://BACKEND_PRIVATE_OR_PUBLIC_IP/api/v1
```

Then replace it with API Gateway after the API Gateway deployment is complete.

## Backend EC2 Deployment

Install Docker:

```bash
sudo yum update -y
sudo yum install -y docker git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user
```

Clone repository:

```bash
git clone https://github.com/Battleboy-bot/aws-cloud-notes-storage-system-3-layer-architecture.git
cd aws-cloud-notes-storage-system-3-layer-architecture
```

Build and run backend:

```bash
docker build -t notes-backend ./backend
docker run -d --name notes-backend --restart unless-stopped \
  -p 80:80 \
  -e AWS_REGION=eu-north-1 \
  -e S3_BUCKET_NAME=aws-cloud-notes-storage-oobat \
  -e DB_SECRET_ID=prod/notes/db \
  -e ALLOWED_ORIGINS=http://FRONTEND_PUBLIC_IP \
  notes-backend
```

The backend EC2 must use the IAM role. Do not put AWS access keys on the server.

## Database Schema

Connect to RDS from a temporary admin machine or MySQL client and run:

```bash
mysql -h YOUR_RDS_ENDPOINT -u notes_user -p < database/schema.sql
```

## API Gateway Final Step

After frontend, backend, RDS, and S3 work:

1. Create an internal Network Load Balancer for backend EC2.
2. Create an API Gateway VPC Link to the internal NLB.
3. Create a Private API Gateway.
4. Import `docs/aws/api-gateway-openapi.yaml`.
5. Replace placeholder values.
6. Deploy the API.
7. Update the frontend container with the API Gateway URL.

Restart frontend after changing API URL:

```bash
docker stop notes-frontend
docker rm notes-frontend
docker run -d --name notes-frontend --restart unless-stopped \
  -p 80:80 \
  -e API_BASE_URL=https://YOUR_API_GATEWAY_URL/api/v1 \
  notes-frontend
```

## Validation

Check frontend:

```text
http://FRONTEND_PUBLIC_IP
```

Check backend health:

```bash
curl http://BACKEND_IP/health
```

Check containers:

```bash
docker ps
```

Expected containers:

```text
notes-frontend on frontend EC2
notes-backend on backend EC2
RDS MySQL as separate managed database instance
```
