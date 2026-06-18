## Requirement Understanding
Deploy a containerized, cloud-native application using:
API + Database on  Kubernetes

The system must prioritize:
- High availability  
- Automatic scaling (HPA)  
- Persistent data storage (StatefulSets)  
- Secure configuration management  

## Assumptions
- The cluster operates in the `default` namespace.
- All container images are stored in a public/accessible Docker registry.
- Persistent storage is provisioned via the cluster's default `StorageClass`.

## Solution Overview
- A **LoadBalancer Ingress** routes external traffic.
- Traffic hits the **API Service**, which uses connection pooling.
- The API interacts with a **PostgreSQL StatefulSet**.
- Configuration is managed using `ConfigMaps` and `Secrets`.



# Justification for Resources Utilized

## StatefulSet
- Ensures stable network identity
- Supports persistent storage for database

## HPA (Horizontal Pod Autoscaler)
- Scales based on real-time demand
- Optimizes infrastructure cost (FinOps)

## ConfigMaps & Secrets
- Separates configuration from code
- Improves portability and security

## Readiness Probes
- Prevents traffic routing to unready pods
- Enables zero-downtime deployments

## 1Gi Persistent Disk
- Balanced choice between:
  - Data durability  
  - Cost efficiency  

---

# My Approach to the Solution

## Step 1: Creting the Python based Application
I created the python application and tested it using a docker-compose in local WSL.
Once the appiation was working, I built the docker image and pushed it to Docker HUB

A Python Flask application was built for simplicity and performance.

- **app.py:**  
  Contains routing, business logic, and DB connection pooling using `psycopg2`.

- **requirements.txt:**  
  Lists project dependencies.

- **Dockerfile:**  
  Defines the container build process to ensure consistency.

---

## Step 2: Build and Push Docker Images

### Build Image
```bash
docker build -t ankushshwork/api-service:v2 .
```

### Push Image
```bash
docker push ankushshwork/api-service:v2
```

---
## Step 3: Creating the Database in Kubernetes
The database initialization script is defined as a **ConfigMap** in the Kubernetes manifest (`02-database.yaml`).

- **Logic:**  
  The database must include a table with 5–10 records at startup.

- **Mechanism:**  
  - The init script is embedded in a ConfigMap named `db-init-script`
  - The ConfigMap is mounted as a volume to:
    ```
    /docker-entrypoint-initdb.d
    ```
  - PostgreSQL executes it automatically during first initialization
  
- **Implementation:**  
  The ConfigMap contains SQL commands to:
  - Create the `NAGAP_USER_INFO` table
  - Insert 10 sample user records with technology bands and status

---

## Step 4: GKE Configuration (ConfigMaps and Secrets)

Used Kubernetes-native configuration management:

- **ConfigMap**
  - Stores non-sensitive data (e.g., `DB_HOST`)
  - Uses `db-service` for internal DNS resolution

- **Secret**
  - Stores sensitive data (e.g., `DB_PASSWORD`)
  - Base64 encoded and injected as environment variables

### Apply Configuration
```bash
kubectl apply -f k8s/01-config-secrets.yaml
```

---

## Step 5: Persistent Database Tier

PostgreSQL deployed using **StatefulSet** with integrated initialization.

### Key Features

- **Initialization Script**
  - ConfigMap `db-init-script` contains the SQL initialization script
  - Mounted to `/docker-entrypoint-initdb.d` for automatic execution
  - Creates table and inserts 10 user records on first startup

- **Persistence**
  - Uses `volumeClaimTemplates`
  - Requests 1Gi persistent storage

- **Environment Fix**
  - Configured:
  ```
  PGDATA=/var/lib/postgresql/data/pgdata
  ```
  to avoid filesystem conflicts

### Apply Manifest
```bash
kubectl apply -f k8s/02-database.yaml
```

This manifest includes:
- ConfigMap with database initialization script
- StatefulSet for PostgreSQL
- ClusterIP Service for internal communication

---

## Step 6: API Service Deployment

API deployed with **4 replicas** for high availability.

### Key Features

- **FinOps Optimization**
  - Memory: 64Mi – 128Mi  
  - CPU: 100m – 250m  

- **Self-Healing**
  - `livenessProbe`
  - `readinessProbe`
  - Endpoint: `/healthz`

### Apply Manifest
```bash
kubectl apply -f k8s/03-api-service.yaml
```

---

## Step 7: Routing and Scaling

### Components Implemented

- **Horizontal Pod Autoscaler (HPA)**
  - Scales pods dynamically based on CPU usage

- **Ingress**
  - Acts as a single entry point for external traffic

### Apply Manifest
```bash
kubectl apply -f k8s/04-ingress-hpa.yaml
```

---

