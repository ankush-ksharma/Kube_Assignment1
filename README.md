# Amy Approach to the Solution

### Step 1 Creating the Database
Init.sql file will create dataabased with some data

Writing standard SQL to create a table and insert 10 rows of data.
The assignment strictly requires the Database Tier to "include one table with 5–10 records" immediately when it starts. We will tell Kubernetes to run this script later when it launches the database.

### Step 2 Creating the API Application
I created a Python BAsed applciation to show this data using flash and PostgresSQL adapter.
This has 
app.py with falsh code
requirements.txt - dependencies

Docker file - with steps to run it in a docker

### Step 3 Build and Push docker images
1. Build the container image using your exact Docker Hub tag
```docker build -t ankushshwork/api-service:v2 .```
2. Push it to your repository
```docker push ankushshwork/api-service:v2```

### Step 4 Create GKE with Standard Settings and 3 nodes
Use UI to create the GKE
Once done connect using the command 
```gcloud container clusters get-credentials nagap-cluster --zone asia-east1-a --project project-ef764628-4e1c-4d77-916```
Once Done, check status of nodes 
```kubectl get nodes```
Once they are ready create a ConfigMap and Secrets

ConfigMap is a native Kubernetes dictionary storage object used to hold non-confidential configuration settings in key-value pairs.
This satisfies the core architectural rule: "Database configuration... should be configurable from outside the pod definition file and application code". By pointing DB_HOST to db-service, your Python application automatically searches the cluster's internal CoreDNS system to find the database. If your database moves to a different machine, you only update this single ConfigMap entry—you never have to modify or rebuild your Python container code.

Kubernetes Secret is a secure object specifically designed to store sensitive data like passwords, tokens, or keys.
By converting the password into a Base64 string (U3VwZXJTZWN1cmVQYXNzd29yZDEyMyE=), someone looking over your shoulder or browsing your GitHub repository cannot easily see your production database credentials. When Kubernetes injects this secret into your Python container later, it automatically decodes it back to plain text in-memory, ensuring your Flask code reads it seamlessly.

Then run 
```
kubectl apply -f k8s/01-config-secrets.yaml 
configmap/app-config created
secret/db-secret created
ankush_sh_work@cloudshell:~/NAGP_Assignment1$ kubectl get configmap app-config
NAME         DATA   AGE
app-config   4      11s
ankush_sh_work@cloudshell:~/NAGP_Assignment1$ kubectl get secret db-secret
NAME        TYPE     DATA   AGE
db-secret   Opaque   1      21s
```

### Step 5 The Persistent Database Tier.
Create the Database Manifest File (02-database.yaml)
Here is the complete, high-detail structural breakdown for Phase 4: The Persistent Database Tier, formatted exactly like the previous phase. This contains the updated, working configuration that resolves the GCP disk storage error.

Phase 4: Deploying the Persistent Database Tier (PostgreSQL)
In this phase, we act as a Database Infrastructure Engineer. We are going to deploy a secure, self-healing, and persistent PostgreSQL database inside your GKE cluster. This configuration automatically spins up a real Google Cloud storage drive, initializes your 10 custom NAGP records on startup, and isolates the database from the public internet.

Step 1: Create the Database Manifest File (02-database.yaml)
In your k8s folder inside VS Code, open your 02-database.yaml file and ensure it contains this exact config:

YAML
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-init-script
  namespace: default
data:
  init.sql: |
    CREATE TABLE IF NOT EXISTS NAGAP_USER_INFO (
        id SERIAL PRIMARY KEY,
        candidate_name VARCHAR(100) NOT NULL,
        technology_band VARCHAR(100) NOT NULL,
        status VARCHAR(100) NOT NULL
    );

    INSERT INTO NAGAP_USER_INFO (candidate_name, technology_band, status) VALUES
    ('User1', 'TechnologyBand1', 'PotentailNAGP'),
    ('User2', 'TechnologyBand1', 'TaggedNAGAP'),
    ('User3', 'QABand1', 'PotentailNAGP'),
    ('User4', 'QABand1', 'TaggedNAGAP'),
    ('User5', 'ITBand1', 'PotentailNAGP'),
    ('User6', 'ITBand2', 'TaggedNAGAP'),
    ('User7', 'DEVOPSBand1', 'PotentailNAGP'),
    ('User8', 'DEVOPSBand2', 'TaggedNAGAP'),
    ('User9', 'DEVOPSBand2', 'PotentailNAGP'),
    ('User10', 'DEVOPSBand2', 'TaggedNAGAP')
    ON CONFLICT DO NOTHING;
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-db
  namespace: default
spec:
  serviceName: "db-service"
  replicas: 1 
  selector:
    matchLabels:
      app: postgres-db
  template:
    metadata:
      labels:
        app: postgres-db
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: DB_NAME
        - name: POSTGRES_USER
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: DB_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: DB_PASSWORD
        ports:
        - containerPort: 5432
          name: dbport
        volumeMounts:
        - name: db-data
          mountPath: /var/lib/postgresql/data
        - name: init-script
          mountPath: /docker-entrypoint-initdb.d
      volumes:
      - name: init-script
        configMap:
          name: db-init-script
  volumeClaimTemplates:
  - metadata:
      name: db-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi 
---
apiVersion: v1
kind: Service
metadata:
  name: db-service
  namespace: default
spec:
  ports:
  - port: 5432
  selector:
    app: postgres-db
  type: ClusterIP
Detailed Breakdown of Step 1:
The Init Script ConfigMap (db-init-script):

What you are doing: Writing your raw SQL schema and seeding data directly into a Kubernetes configuration string, then mounting it inside the container's /docker-entrypoint-initdb.d path.

Why: This satisfies the database requirements to include a table seeded with 5–10 records. PostgreSQL natively triggers any .sql scripts found in this specific directory when the cluster starts for the first time.

The StatefulSet Architecture (kind: StatefulSet):

What you are doing: Deploying the database using a StatefulSet controller restricted to exactly replicas: 1.

Why: This satisfies the requirements: "Number of pods: 1" and "Automatically recover after pod deletion". Unlike standard deployments, a StatefulSet gives the pod a permanent, unique name (postgres-db-0). If the pod dies, Kubernetes revives it and safely hooks it back up to its exact historical data disk.

The GCP Disk Subdirectory Fix (name: PGDATA):

What you are doing: Setting the database storage directory path to a clean sub-folder (/var/lib/postgresql/data/pgdata).

Why: This prevents the standard Google Cloud platform crash where the raw Linux file system recovery folder (lost+found) breaks the standard Postgres initializer.

The Dynamic Storage Disk Request (volumeClaimTemplates):

What you are doing: Requesting a 1 Gigabyte persistent block storage volume from Google Cloud using ReadWriteOnce access rules.

Why: This handles the data persistence constraint ("Database data should not be lost if the pod for database is re-deployed"). Allocating a lean 1Gi instead of an over-provisioned 20Gi disk satisfies your project's data scale while practicing smart FinOps resource conservation.

The Cluster IP Firewall Protection (type: ClusterIP):

What you are doing: Restricting the database network access point directly inside the cluster's internal network using a headless reference.

Why: This satisfies the conditions: "Be accessible only within the cluster (Exposed outside the cluster: No)" and "Pod IPs should not be used for communication between tiers". It maps a permanent cluster DNS link (db-service) that your Python API pods can use safely without exposing your data assets to public internet threats.

Apply using 
```
kubectl apply -f k8s/02-database.yaml
kubectl get pvc
kubectl get pods
```

### Step 6 Crete API Menifest
The Replicas Count (replicas: 4):

What you are doing: Telling Kubernetes to maintain exactly 4 simultaneous running copies (pods) of your Python UI application.

Why: This directly satisfies the assignment requirement: "Service API Tier Number of pods: 4". Running 4 copies ensures high availability—if a hosting server crashes, the remaining pods keep serving the user interface with zero downtime.

The ConfigMap & Secret Injection (valueFrom):

What you are doing: Binding the DB_HOST, DB_NAME, DB_USER, and DB_PASSWORD keys from Phase 3 directly into the environment variables of your Python container.

Why: This fulfills the rule: "The database configuration... should be configurable from outside the pod definition file and application code". Your app.py script pulls these variables seamlessly via standard Python instructions without hardcoding credentials.

FinOps Resource Allocation (resources):

What you are doing: Defining the precise memory (64Mi to 128Mi) and CPU (100m to 250m) constraints for each pod.

Why: This satisfies the FinOps condition: "Define CPU and memory requests and limits for the Service/API tier." Setting a strict limit of 128Mi keeps the application from consuming excess cluster memory, allowing Google Cloud to tightly pack your cluster nodes and significantly lower cloud runtime costs.

Self-Healing Mechanics (livenessProbe & readinessProbe):

What you are doing: Directing the cluster's health tracker to ping the internal /healthz route on your Python web server every 5 seconds.

Why: This proves the Self-Healing criteria. If your Python application suffers an unexpected process deadlock, the liveness probe fails, and the cluster immediately destroys and replaces the broken pod with a fresh container.

Run 
```
kubectl apply -f k8s/03-api-service.yaml
```
```
kubectl get pods
```

### Step 7 Creat Routing Menifest
04-ingress-hpa.yaml

Then apply using 
```
kubectl apply -f k8s/04-ingress-hpa.yaml
```
And check using 
```
kubectl get hpa
kubectl get ingress
```