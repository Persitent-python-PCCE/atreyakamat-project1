# Kubernetes RollingUpdate Rollout Simulation & Probe Guide

This document details the complete step-by-step code changes, container build, and live simulation of a **Zero-Downtime Kubernetes RollingUpdate Rollout** using `maxSurge`, `maxUnavailable`, and `livenessProbe` / `readinessProbe`.

---

## 1. Code Changes Made (Version `v1.0.0` ➔ `v2.0.0`)

To simulate a real-world release, we updated the `/health` endpoint in [`Controller/home_controller.py`](file:///home/atreya/Projects/atreyakamat-project1/Controller/home_controller.py) to return version metadata for Kubernetes health probes.

### Updated Endpoint Code (`Controller/home_controller.py`):
```python
@home_bp.route("/health")
def health():
    """Health check endpoint for Kubernetes liveness & readiness probes."""
    return {
        "status": "ok",
        "service": "SeatMeUp",
        "version": "2.0.0",
        "deployment": "rolling-update-v2",
    }
```

---

## 2. Updated Kubernetes Manifest (`k8s/flask-deployment.yaml`)

The deployment was updated with **3 replicas**, a **RollingUpdate strategy** (`maxSurge: 1`, `maxUnavailable: 1`), **Liveness & Readiness Probes**, and image tag `atreya7/seatmeup:v2`.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: flask
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
        - name: flask
          image: atreya7/seatmeup:v2
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          
          # Liveness Probe: Restarts container if /health fails
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10

          # Readiness Probe: Routes traffic only after /health responds HTTP 200
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10

          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: MYSQL_DB_URL
            - name: MYSQL_DB_URL
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: MYSQL_DB_URL
            - name: FLASK_ENV
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DEPLOYMENT_ENV
```

---

## 3. How RollingUpdate Math Works (`replicas: 3`)

Given:
- `replicas`: **3**
- `maxSurge`: **1** *(Maximum 3 + 1 = 4 total pods during rollout)*
- `maxUnavailable`: **1** *(Minimum 3 - 1 = 2 healthy pods serving user traffic at all times)*

```
Step 0:  [Pod-v1-A] [Pod-v1-B] [Pod-v1-C]               (3 Running v1 pods)
Step 1:  [Pod-v1-A] [Pod-v1-B] [Pod-v1-C] [Pod-v2-1]    (Surge +1 new v2 pod created -> 4 pods total)
Step 2:  Readiness probe passes on [Pod-v2-1]
Step 3:  [Pod-v1-A] [Pod-v1-B] [Pod-v2-1] [Pod-v2-2]    (Old pod [Pod-v1-C] terminated, 2nd v2 pod created)
Step 4:  [Pod-v1-A] [Pod-v2-1] [Pod-v2-2] [Pod-v2-3]    (Old pod [Pod-v1-B] terminated, 3rd v2 pod created)
Step 5:  [Pod-v2-1] [Pod-v2-2] [Pod-v2-3]               (Final state: 3 healthy v2 pods, 0 downtime)
```

---

## 4. Execution Commands Used

```bash
# 1. Build the v2 container image
docker build -t atreya7/seatmeup:v2 .

# 2. Import image into Kind cluster containerd runtime
docker save atreya7/seatmeup:v2 | docker exec -i seatmeup-cluster-control-plane ctr -n k8s.io images import -

# 3. Apply the updated deployment manifest
kubectl apply -f k8s/flask-deployment.yaml

# 4. Monitor rollout status live
kubectl rollout status deployment/flask-deployment

# 5. Check running pods
kubectl get pods -l app=flask

# 6. Verify health endpoint returns version 2.0.0
curl -s http://localhost:30007/health
```

---

## 5. Live Simulation Execution Output

### Rollout Command Output:
```bash
$ kubectl rollout status deployment/flask-deployment
Waiting for deployment "flask-deployment" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "flask-deployment" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "flask-deployment" rollout to finish: 2 of 3 updated replicas are available...
deployment "flask-deployment" successfully rolled out
```

### Pod Status Output (3/3 Ready):
```bash
$ kubectl get pods -l app=flask
NAME                              READY   STATUS    RESTARTS   AGE
flask-deployment-984c894f-hcsnm   1/1     Running   0          21s
flask-deployment-984c894f-nct4w   1/1     Running   0          21s
flask-deployment-984c894f-zp58h   1/1     Running   0          10s
```

### Live Health Endpoint Verification Output:
```bash
$ curl -s http://localhost:30007/health
{
  "deployment": "rolling-update-v2",
  "service": "SeatMeUp",
  "status": "ok",
  "version": "2.0.0"
}
```

---

## 6. How to Rollback if a Deployment Fails (`Rollback Simulation`)

If a new version contains a critical bug, Kubernetes lets you instantly roll back to the previous stable revision:

```bash
# View rollout revision history
kubectl rollout history deployment/flask-deployment

# Roll back to previous revision (Revision 3 -> Revision 2)
kubectl rollout undo deployment/flask-deployment

# Roll back to a specific revision
kubectl rollout undo deployment/flask-deployment --to-revision=1
```
