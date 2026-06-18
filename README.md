# My Approach to the Solution

1. Link for the code repository
[GitHub Repository](https://github.com/ankush-ksharma/Kube_Assignment1.git)

2. Docker hub URL for docker images.
[Docker Hub](https://hub.docker.com/repository/docker/ankushshwork/api-service/general)
  ```docker push ankushshwork/api-service:v3```

3. URL for Service API tier to view the records from backend tier.
[NAGP Dashboard](http://35.227.218.255/)

4. Screen Recording


---
---
## Answers to FinOps Requirements

### 1. Define CPU and memory requests and limits for the Service/API tier.
In Kubernetes, these settings dictate the Quality of Service (QoS) of your pods.

Requests (The "Reserved" Amount): This is the minimum amount of CPU and memory the node guarantees to the container. The Kubernetes scheduler uses this number to decide which node your pod lands on.

Limits (The "Hard Cap"): This is the maximum resources the container is allowed to consume. If a container tries to exceed its memory limit, it will be terminated (OOMKilled).
---
### Implementation: API Tier Manifest
In 03-api-service.yaml under the containers section:

```
resources:
  requests:
    memory: "64Mi"  # Start here, increase if OOMKilled
    cpu: "100m"     # 0.1 vCPU
  limits:
    memory: "128Mi" # Hard limit
    cpu: "250m"     # 0.25 vCPU
```

---

### 2. Three Opportunities to Optimize Kubernetes Costs
1. Right-Sizing (VPA) - Use tools like the Vertical Pod Autoscaler or metrics to analyze actual usage. If your "Request" is 500m CPU but your app only uses 50m, you are wasting 90% of the allocated capacity. Reduce the requests to match reality.
2. Cluster Autoscaling - Enable the Cluster Autoscaler in GKE. It monitors for unscheduled pods and adds nodes only when necessary. Conversely, it deletes nodes when they are empty, preventing you from paying for idle compute VMs.Spot Instances
3. Use Spot VMs (or Preemptible VMs) for your stateless API tier. These are ~60-90% cheaper than standard VMs. Since your API is stateless and scalable (4 replicas), if one node is reclaimed, the remaining pods/HPA will handle the load.

---
### 3. Implementing Optimization Using Metrics
You cannot optimize what you do not measure. To fine-tune your requests and limits, follow this Observability Loop:

Step A: Gather Observed Data
Use the Kubernetes Metrics Server to view real-time usage. Run this command in your cloud shell:


View current usage of pods in the namespace
```
kubectl top pods
```

Look for: The difference between the Request (what you asked for) and Usage (what is actually being used). If Usage is consistently 10% of the Request, you are over-provisioned.

- Start Low: Set requests slightly above the average usage.
- Monitor: Run the app under load for 24 hours.
- Adjust: If the app is stable, lower the requests to match the 95th percentile of usage.
- Repeat: If the app becomes unstable or slow, increase resources in small, documented increments.