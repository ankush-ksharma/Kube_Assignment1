# GKE Kubernetes Deployment Demonstration Script

This script guides you through demonstrating all Kubernetes features for your screen recording.

---

## Prerequisites

Before starting the recording:
```bash
# Connect to your GKE cluster
gcloud container clusters get-credentials <your-cluster-name> --region <your-region> --project <your-project>

# Verify connection
kubectl cluster-info
```

---

## 🎬 SECTION 1: Show All Deployed Objects (2-3 minutes)

### 1.1 Show All Kubernetes Resources

```bash
# Show all resources in the cluster
kubectl get all

# Expected output:
# - Deployment: api-deployment (with 4 pods)
# - StatefulSet: postgres-db (with 1 pod)
# - Services: api-service, db-service
# - Pods: 4 API pods + 1 DB pod
# - ReplicaSets
```

### 1.2 Show Detailed Resource Information

```bash
# Show ConfigMaps
kubectl get configmap
kubectl describe configmap app-config

# Show Secrets
kubectl get secrets
kubectl describe secret db-secret

# Show Persistent Volume Claims (for database)
kubectl get pvc
kubectl describe pvc db-storage-postgres-db-0

# Show Ingress
kubectl get ingress
kubectl describe ingress app-ingress

# Show HorizontalPodAutoscaler
kubectl get hpa
kubectl describe hpa api-hpa
```

### 1.3 Show Pod Details

```bash
# Show API deployment pods
kubectl get pods -l app=api-service -o wide

# Show database StatefulSet pod
kubectl get pods -l app=postgres-db -o wide

# Show detailed info about one API pod
kubectl describe pod <api-pod-name>
```

### 1.4 Show Deployment Strategy

```bash
# Show deployment strategy (RollingUpdate)
kubectl describe deployment api-deployment | grep -A 5 "StrategyType"

# Expected output shows:
# - RollingUpdate strategy
# - MaxSurge: 1
# - MaxUnavailable: 0
```

---

## 🎬 SECTION 2: API Call Retrieving Database Records (2 minutes)

### 2.1 Get Ingress External IP

```bash
# Get the external IP address
kubectl get ingress app-ingress

# Wait until ADDRESS field shows an IP (may take a few minutes)
# Note down the EXTERNAL_IP
```

### 2.2 Make API Calls

#### Option A: Using Browser
```
# Open browser and navigate to:
http://<EXTERNAL_IP>/

# This shows the web interface with all candidate records

# For JSON API response, navigate to:
http://<EXTERNAL_IP>/api/data
```

#### Option B: Using curl
```bash
# Get the Ingress IP
INGRESS_IP=$(kubectl get ingress app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Call the API endpoint
curl http://$INGRESS_IP/api/data

# Or with formatting
curl -s http://$INGRESS_IP/api/data | python3 -m json.tool

# Call the web interface
curl http://$INGRESS_IP/
```

### 2.3 Show Database Query Results

**Narrate:** "This data is coming from our PostgreSQL database running in a StatefulSet with persistent storage. The API service queries the NAGAP_USER_INFO table containing 10 candidate records."

---

## 🎬 SECTION 3: Kill API Pod and Show Self-Healing (3 minutes)

### 3.1 Get Current Pod Status

```bash
# List all API pods and their status
kubectl get pods -l app=api-service -w &

# Note: -w flag watches for changes in real-time
# Keep this running in a separate terminal
```

### 3.2 Delete an API Pod

```bash
# In another terminal, get pod names
kubectl get pods -l app=api-service

# Delete one pod
kubectl delete pod <api-pod-name>

# Example:
# kubectl delete pod api-deployment-7d8f9b6c4-abc12
```

### 3.3 Observe Self-Healing

**Watch the first terminal with -w flag:**
- You'll see the pod enter "Terminating" state
- Kubernetes immediately creates a new pod
- New pod goes through: Pending → ContainerCreating → Running
- Deployment maintains 4 replicas at all times

```bash
# Stop the watch (Ctrl+C) and verify all pods are running
kubectl get pods -l app=api-service

# Show deployment status
kubectl rollout status deployment api-deployment
```

### 3.4 Verify API Still Works

```bash
# Make another API call to verify service continuity
curl http://$INGRESS_IP/api/data
```

**Narrate:** "Notice how Kubernetes immediately recreated the pod. The ReplicaSet controller ensures we always have 4 replicas running. The service remained available throughout because other pods continued serving traffic."

---

## 🎬 SECTION 4: Kill Database Pod and Show Data Persistence (4 minutes)

### 4.1 Verify Current Data

```bash
# First, show current data via API
curl http://$INGRESS_IP/api/data

# Count records
curl -s http://$INGRESS_IP/api/data | python3 -c "import sys, json; print(f\"Total records: {len(json.load(sys.stdin)['data'])}\")"
```

### 4.2 Add New Data (Optional but Impressive)

```bash
# Access the web interface and add a new candidate
# Or use kubectl exec to insert data directly

# Get database pod name
DB_POD=$(kubectl get pods -l app=postgres-db -o jsonpath='{.items[0].metadata.name}')

# Insert a test record
kubectl exec -it $DB_POD -- psql -U postgres -d nagp_db -c \
  "INSERT INTO NAGAP_USER_INFO (candidate_name, technology_band, status) VALUES ('TestUser', 'TestBand', 'PotentailNAGP');"

# Verify insertion
curl http://$INGRESS_IP/api/data | grep TestUser
```

### 4.3 Watch Database Pod

```bash
# Watch database pod in one terminal
kubectl get pods -l app=postgres-db -w
```

### 4.4 Delete Database Pod

```bash
# In another terminal, delete the database pod
kubectl delete pod $DB_POD

# Or simply:
# kubectl delete pod postgres-db-0
```

### 4.5 Observe Self-Healing

**Watch the terminal with -w flag:**
- Pod enters "Terminating" state
- StatefulSet controller creates new pod with SAME NAME (postgres-db-0)
- Pod goes through initialization
- Pod mounts the SAME PersistentVolume

```bash
# After pod is running, check status
kubectl get pods -l app=postgres-db
kubectl get pvc

# Notice the PVC age didn't change - same volume reattached
```

### 4.6 Verify Data Persistence

```bash
# Wait for pod to be ready
kubectl wait --for=condition=ready pod/postgres-db-0 --timeout=120s

# Verify data is still there
curl http://$INGRESS_IP/api/data

# Check for the test record if you inserted one
curl -s http://$INGRESS_IP/api/data | python3 -c "import sys, json; print(f\"Total records: {len(json.load(sys.stdin)['data'])}\")"

# Or exec into the new pod
kubectl exec -it postgres-db-0 -- psql -U postgres -d nagp_db -c "SELECT COUNT(*) FROM NAGAP_USER_INFO;"
```

**Narrate:** "The data persisted because the StatefulSet uses a PersistentVolumeClaim. When the pod was recreated, it reattached to the same persistent volume. This demonstrates how StatefulSets maintain stable storage for stateful applications like databases."

---

## 🎬 SECTION 5: Advanced Demonstrations (3-4 minutes)

### 5.1 Deployment Strategy (RollingUpdate)

```bash
# Show current deployment details
kubectl describe deployment api-deployment

# Trigger a rolling update by changing the image tag
kubectl set image deployment/api-deployment flask-api=ankushshwork/api-service:v3

# Watch the rolling update in action
kubectl rollout status deployment api-deployment -w

# Check rollout history
kubectl rollout history deployment api-deployment
```

**Narrate:** "The RollingUpdate strategy ensures zero downtime. With maxSurge=1 and maxUnavailable=0, Kubernetes creates one new pod before terminating an old one, ensuring we always have at least 4 pods serving traffic."

### 5.2 Horizontal Pod Autoscaling

```bash
# Show HPA configuration
kubectl get hpa api-hpa

# Show current CPU usage and replica count
kubectl top pods -l app=api-service

# Describe HPA
kubectl describe hpa api-hpa
```

**Narrate:** "The HPA monitors CPU utilization and automatically scales the deployment between 4 and 10 replicas. When CPU exceeds 50%, it adds more pods. This ensures optimal performance under load while managing costs."

### 5.3 Resource Management & FinOps

```bash
# Show resource requests and limits
kubectl describe deployment api-deployment | grep -A 10 "Limits"

# Show total resource allocation
kubectl top nodes
kubectl top pods -l app=api-service
```

**Narrate the FinOps considerations:**

1. **Resource Requests/Limits:** 
   - CPU: 100m request, 250m limit per pod
   - Memory: 64Mi request, 128Mi limit per pod
   - Prevents resource waste and ensures predictable costs

2. **Right-sizing:**
   - Database: 1Gi storage (can be increased as needed)
   - API pods: Minimal resources for cost efficiency

3. **Autoscaling:**
   - Min 4 replicas for high availability
   - Max 10 replicas to cap costs
   - Scale based on actual CPU usage

4. **Storage:**
   - Only database uses persistent storage
   - API is stateless, no storage overhead

5. **RollingUpdate Strategy:**
   - maxUnavailable=0 prevents downtime
   - maxSurge=1 minimizes temporary resource spike

### 5.4 Health Checks

```bash
# Show liveness and readiness probes
kubectl describe deployment api-deployment | grep -A 3 "Liveness"
kubectl describe deployment api-deployment | grep -A 3 "Readiness"

# Test health endpoint directly
API_POD=$(kubectl get pods -l app=api-service -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $API_POD -- curl localhost:3000/healthz
```

---

## 🎬 SECTION 6: Final Summary (1 minute)

### Show Everything Running Healthy

```bash
# Final status check
kubectl get all

# Show deployment health
kubectl get deployments
kubectl get statefulsets
kubectl get pvc

# Show HPA status
kubectl get hpa

# Make final API call
curl http://$INGRESS_IP/api/data
```

---

## 📋 Key Points to Narrate

### Self-Healing
- ✅ **API Pods:** ReplicaSet ensures desired count (4) is always maintained
- ✅ **Database Pod:** StatefulSet recreates with same identity and persistent volume

### Persistence
- ✅ **Database:** PersistentVolumeClaim survives pod restarts
- ✅ **Data Integrity:** All data remains intact after pod deletion

### Deployment Strategy
- ✅ **RollingUpdate:** Zero-downtime deployments
- ✅ **MaxSurge=1, MaxUnavailable=0:** Gradual rollout with no service interruption

### FinOps Considerations
- ✅ **Resource Limits:** Prevents runaway costs
- ✅ **HPA:** Scales based on demand (4-10 replicas)
- ✅ **Right-sizing:** Minimal resources for efficiency
- ✅ **Cost Predictability:** Capped at 10 max replicas

### High Availability
- ✅ **4 API replicas:** Load distribution and fault tolerance
- ✅ **Health Checks:** Automatic restart of unhealthy pods
- ✅ **LoadBalancer/Ingress:** Traffic distribution across pods

---