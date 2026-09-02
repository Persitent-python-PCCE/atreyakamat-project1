# From Local Code to Docker & Kubernetes: A Beginner's Complete Guide

Welcome! This document provides a complete, step-by-step guide explaining how **SeatMeUp** was built, containerized, and deployed from local Python development to **Docker Compose** and a **Kubernetes** cluster.

---

## 🗺️ Architectural Overview

```
┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│  1. LOCAL DEVELOPMENT   │      │   2. DOCKER CONTAINERS  │      │  3. KUBERNETES CLUSTER  │
│  • Python Virtual Env   │ ───► │  • Dockerfile           │ ───► │  • Kind Cluster         │
│  • System MariaDB/MySQL │      │  • Docker Hub Image     │      │  • Deployments & Pods   │
│  • Local .env Config    │      │  • Docker Compose Stack │      │  • NodePort & Secrets   │
└─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 1. Local Development Setup

In local development, the application runs directly on your host operating system:
- **Flask App**: Runs inside Python virtual environment (`.venv`) using `flask run --port 8000`.
- **MySQL / MariaDB**: Runs locally on host port `3306`.
- **Environment Config**: Loaded from `.env` file (`DATABASE_URL=mysql+pymysql://atreya:atreya@localhost:3306/seatmeup`).

### Crucial Fixes Applied:
1. **Module-Level `app` Export (`app.py`)**:
   - Gunicorn and WSGI servers require `app` to be exported at the top level of `app.py`.
   ```python
   # app.py
   app = create_app()

   if __name__ == "__main__":
       app.run(debug=True)
   ```
2. **Auto Table Creation (`scripts/seed_demo_data.py`)**:
   - Added `db.create_all()` inside `seed_data()` so database tables are automatically initialized prior to populating user and event data.

---

## 2. Docker Containerization & Docker Hub

### The Production `Dockerfile`
The `Dockerfile` defines how to package the app into a reproducible container image:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code & create upload directories
COPY . /app/
RUN mkdir -p /app/uploads /app/static/uploads/event_posters /app/static/generated_tickets /app/instance

EXPOSE 8000

# Start WSGI Server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Building & Pushing Images
```bash
# Build the Docker image
docker build -t atreya7/seatmeup:latest -t atreya7/seatmeup:1.0.0 .

# Push to Docker Hub
docker push atreya7/seatmeup:latest
docker push atreya7/seatmeup:1.0.0
```

---

## 3. Multi-Container Orchestration with Docker Compose

### Avoiding Port Conflicts (`3307:3306`)
If your host computer already runs MariaDB/MySQL on port `3306`, mapping `3306:3306` in Docker Compose will cause a port collision error (`failed to bind host port 0.0.0.0:3306/tcp: address already in use`).

**Solution:** Map the database container to host port `3307`:

```yaml
# docker-compose.yml
services:
  db:
    image: mysql:latest
    container_name: seatmeup-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: atreya
      MYSQL_DATABASE: seatmeup
      MYSQL_USER: atreya
      MYSQL_PASSWORD: atreya
    ports:
      - "3307:3306"   # Host 3307 -> Container 3306
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - seatmeup-net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-patreya"]
      interval: 3s
      timeout: 2s
      retries: 10

  web:
    image: atreya7/seatmeup:latest
    container_name: seatmeup-web
    restart: always
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: mysql+pymysql://atreya:atreya@db:3306/seatmeup
      DB_HOST: db
      DB_PORT: 3306
      DB_USER: atreya
      DB_PASSWORD: atreya
      DB_NAME: seatmeup
      FLASK_ENV: production
      SECRET_KEY: seatmeup-secure-production-secret-key-2026
      JWT_SECRET_KEY: seatmeup-secure-jwt-secret-key-2026
    depends_on:
      db:
        condition: service_healthy
    networks:
      - seatmeup-net

volumes:
  mysql-data:
networks:
  seatmeup-net:
    driver: bridge
```

### Running Docker Compose:
```bash
# Launch containers in background
docker compose up -d

# Seed database inside running web container
docker exec seatmeup-web python scripts/seed_demo_data.py

# Access App in browser
http://localhost:8000
```

---

## 4. Kubernetes (k8s) Deployment

### Manifest Architecture (`k8s/`)

| File | Resource | Purpose |
| :--- | :--- | :--- |
| [`k8s/secret.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/secret.yaml) | **Secret** | Stores encrypted DB password & connection URL (`mysql+pymysql://atreya:atreya@mysql-service:3306/seatmeup`). |
| [`k8s/configmap.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/configmap.yaml) | **ConfigMap** | Stores non-sensitive settings (`MYSQL_HOST: mysql-service`, `MYSQL_DATABASE: seatmeup`). |
| [`k8s/mysql-pvc.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/mysql-pvc.yaml) | **PVC** | Requests 1GB persistent disk storage for MySQL database data. |
| [`k8s/mysql-service.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/mysql-service.yaml) | **Service** | Internal ClusterIP service granting fixed DNS name `mysql-service:3306`. |
| [`k8s/mysql-deployment.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/mysql-deployment.yaml) | **Deployment** | Runs MySQL container connected to Secret, ConfigMap, and PVC storage. |
| [`k8s/flask-deployment.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/flask-deployment.yaml) | **Deployment** | Runs SeatMeUp Flask app pod (`atreya7/seatmeup:latest`). |
| [`k8s/flask-service.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/flask-service.yaml) | **Service** | Exposes the web application externally via NodePort `30007`. |
| [`k8s/kind-config.yaml`](file:///home/atreya/Projects/atreyakamat-project1/k8s/kind-config.yaml) | **Kind Config** | Maps container port `30007` to host port `30007`. |

---

### Bypassing Network Timeouts (Direct Image Transfer)
When deploying locally with Kind, network image downloads inside the node container can time out over slow connections. You can stream host images directly into Kind's `containerd` runtime:

```bash
# Stream local images directly into Kind containerd runtime
docker save mysql:latest | docker exec -i seatmeup-cluster-control-plane ctr -n k8s.io images import -
docker save atreya7/seatmeup:latest | docker exec -i seatmeup-cluster-control-plane ctr -n k8s.io images import -
```

Ensure `imagePullPolicy: IfNotPresent` is set in your deployment YAMLs so Kubernetes uses the imported images instantly.

---

### Step-by-Step Deployment Commands

```bash
# 1. Create Kind cluster with NodePort mapping
kind create cluster --config k8s/kind-config.yaml --name seatmeup-cluster --image kindest/node:v1.31.0

# 2. Import cached docker images into Kind node
docker save mysql:latest | docker exec -i seatmeup-cluster-control-plane ctr -n k8s.io images import -
docker save atreya7/seatmeup:latest | docker exec -i seatmeup-cluster-control-plane ctr -n k8s.io images import -

# 3. Apply all manifests
kubectl apply -f k8s/

# 4. Seed database inside running Kubernetes pod
kubectl exec deployment/flask-deployment -- python -c "from app import app, db; app.app_context().push(); db.create_all(); from scripts.seed_demo_data import seed_data; seed_data()"

# 5. Check cluster pod status
kubectl get pods
kubectl get services
```

---

## 🔑 Demo Access Credentials

- **Kubernetes Access Point**: **`http://localhost:30007`**
- **Docker Compose Access Point**: **`http://localhost:8000`**

### User Accounts (Password for all: `atreya`)
- **Admin**: `atreya@a.com`
- **Customer (Savio Fernandes)**: `savio.fernandes@example.com` (Balance: ₹150.00)
- **Customer (Rohan Naik)**: `rohan.naik@example.com` (Balance: ₹50.00)
- **Customer (Maria D'Souza)**: `maria.dsouza@example.com` (Balance: ₹75.00)
