# 🚀 RoyBrains- MogTok Erp system Development and Deployment with Docker, Nginx, and Certbot

This repository provides a production-ready setup for deploying a RoyBrains- MogTok Erp Django application using **Docker Compose**, **Nginx**, and **Certbot (Let's Encrypt SSL)**.

---

## 📋 Requirements

### For Local (Non-Docker) Development

* Python **3.14+** (Minimum required for better support)
* pip (latest version recommended)

### For Docker Deployment

Before starting, make sure you have:

* Docker
* Docker Compose
* A registered domain name pointing to your server IP

---

## 🖥️ Local Development (Without Docker)

If you want to run the project without Docker:

---

### 1️⃣ Create Virtual Environment (Recommended)

First, create and activate a virtual environment:

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
```

After activation, your terminal should show `(venv)`.

---

### 2️⃣ Install Dependencies

Make sure Python **3.14+** is installed, then run:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3️⃣ Configure Environment Variables

Create a `.env` file and set required values (see below).

---

### 4️⃣ Run Migrations and Server

```bash
python manage.py migrate
python manage.py runserver
```

Your app will be available at:

```
http://127.0.0.1:8000/
```

````

---

## 📁 Environment Configuration

Create a `.env` file in the project root using the following template:

### `.env.example`

```env
DEBUG="PRODUCTION" # PRODUCTION or DEVELOPMENT

# Hosts
# Single: example.com
# Multiple: example.com,learn.example.com
ALLOWED_HOSTS=example.com

# CSRF Trusted Origins
# Single: https://example.com
# Multiple: https://learn.example.com,https://example.com
CSRF_TRUSTED_ORIGINS=https://learn.example.com,https://example.com

# Database (PostgreSQL)
DB_URL=ep-ad-df-182938-pooler.asp-southeast-2.aws.neon.tech
DB_PASS=akjncadlcoirv
DB_USER=admin_mk
DB_NAME=root-db
DB_PORT=5432

# AWS Credentials
AWS_ACCESS_KEY_ID=adcdadsvwvraefefefwr
AWS_SECRET_ACCESS_KEY=acfav/swrvrfvadvrgthrtsdvfgetgh

# S3 Configuration
AWS_STORAGE_BUCKET_NAME=example-bucket
AWS_S3_REGION_NAME=ap-south-1
AWS_S3_SIGNATURE_VERSION=s3v4
AWS_QUERYSTRING_EXPIRE=3600
AWS_S3_CUSTOM_DOMAIN=ajhbcakdhbckdbjv.cloudfront.net
AWS_LOCATION=static
````

> ⚠️ **Important:** Never commit your real `.env` file to GitHub.

---

## ⚙️ Django Database (Development Only)

For local development without password authentication, configure your database in:

### `core/settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'erp-db-one',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```

Use this only in development mode.

---

## 🌐 Nginx Configuration

Edit the domain name in:

### `nginx/nginx.conf`

Replace `{domain.com}` with your actual domain.

```nginx
server_name {domain.com};
```

And in SSL section:

```nginx
ssl_certificate     /etc/letsencrypt/live/{domain.com}/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/{domain.com}/privkey.pem;
server_name {domain.com};
```

### HTTP (Before SSL)

Initially, keep only port **80** enabled to generate SSL certificates.

### HTTPS (After SSL)

Once certificates are generated, uncomment the `443` block and enable HTTPS redirect.

---

## 🔐 Certbot Configuration

Edit `docker-compose.yml` and replace email and domain in the Certbot service.

### Example

```yaml
certbot:
  image: certbot/certbot
  container_name: certbot
  profiles: ["certbot"]
  volumes:
    - ./certbot/conf:/etc/letsencrypt
    - ./certbot/www:/var/www/certbot
  command: certonly --webroot -w /var/www/certbot \
    --email your@email.com \
    -d yourdomain.com \
    --agree-tos
```

Replace:

* `your@email.com`
* `yourdomain.com`

---

## 🐳 Docker Build Dependency Requirement

For successful Docker image builds, **only the following PostgreSQL driver version is supported**:

```
psycopg[c]==3.2.12
```

### ⚠️ Important

Before building Docker images or running `docker compose`, make sure:

* All `psycopg`, `psycopg2`, `psycopg-binary`, or other variants
* Are **replaced with**:

```
psycopg[c]==3.2.12
```

In your `requirements.txt` file.

Example:

```txt
psycopg[c]==3.2.12
```

Failure to do this may cause Docker build errors.

---

## 🚀 Deployment Steps

### 1️⃣ Build and Generate SSL Certificate

Run Certbot profile first:

```bash
docker compose --profile certbot up --build
```

This will:

* Start Nginx
* Verify domain
* Generate SSL certificates

---

### 2️⃣ Enable HTTPS in Nginx

After certificates are created:

1. Uncomment `443` SSL block
2. Enable HTTPS redirect
3. Comment temporary HTTP settings

Then reload containers.

---

### 3️⃣ Start All Services

Run:

```bash
docker compose up -d
```

This will start all production services.

---

### 4️⃣ Restart Services (If Needed)

To stop and restart:

```bash
docker compose down
docker compose up -d
```

---

## 🔄 Re-deployment

If you make changes:

```bash
docker compose down
docker compose up --build -d
```

---

## 📌 Notes

* Make sure your domain DNS is pointing to your server IP
* Ports **80** and **443** must be open
* Certificates are stored in `./certbot/conf`
* Certbot auto-renew can be added later using cron

---

## 🤝 Contribution

Contributions are welcome!

Feel free to:

* Improve documentation
* Add automation
* Enhance security

Create a pull request anytime.

---

## 📞 Support

If you face any issues, open an issue in the repository or contact the maintainer.

Happy Deploying! 🚀
