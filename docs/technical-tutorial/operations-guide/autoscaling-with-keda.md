# Autoscaling with KEDA

Practicus AI supports Kubernetes autoscaling out of the box using **Horizontal Pod Autoscaler (HPA)**.  
For many workloads, CPU or memory-based scaling is sufficient and simple.

However, modern AI and event-driven workloads often need **more advanced scaling signals**—this is where **KEDA** comes in.

---

## What is KEDA?

**KEDA (Kubernetes Event-Driven Autoscaling)** is a Kubernetes add-on that enables autoscaling based on **external and custom metrics**, not just CPU or memory.

Instead of you manually wiring metric adapters, external metrics APIs, and custom HPA logic, KEDA provides:

- A standard Kubernetes resource (`ScaledObject`)
- Built-in integrations for common metric sources
- Automatic HPA creation and management behind the scenes

When you apply a `ScaledObject`, KEDA **creates and owns an HPA** for the target workload and continuously feeds it the right metrics.

---

## When should I use KEDA instead of HPA?

Use **HPA** when:

- CPU or memory utilization is a good proxy for load
- You want the simplest possible setup
- You don’t need scale-to-zero or external metrics

Use **KEDA** when:

- You need to scale on **GPU utilization**
- You want to scale based on **request rate, queue depth, or custom metrics**
- Your metrics come from **Prometheus or external systems**
- You want **event-driven** or **burst-aware** scaling
- You want consistent behavior across different metric types

In short: **HPA is resource-based; KEDA is signal-based.**

---

## How KEDA works (high level)

1. You deploy KEDA into the cluster (operator + metrics adapter)
2. You define a `ScaledObject` that points to a Deployment
3. You define one or more **triggers** (CPU, Prometheus, HTTP, queue, etc.)
4. KEDA:
   - Polls those triggers
   - Exposes metrics to Kubernetes
   - Creates and manages the underlying HPA

You do **not** need to create an HPA yourself when using KEDA.

---

## Important behavior notes

- A Deployment should be managed by **either HPA or KEDA, not both**
- KEDA fully controls the HPA it creates
- You can still fine-tune scale behavior (rate limits, stabilization windows)
- KEDA supports multiple triggers at the same time (e.g. CPU **and** GPU)

---

## Typical AI / Model Hosting use cases

KEDA is especially useful for model-serving workloads where:

- GPU utilization is the true bottleneck
- CPU usage stays low while GPUs saturate
- Load comes in bursts
- Different models have different scaling signals

Common setups include:

- CPU utilization + GPU utilization
- Request rate (RPS) + cool-down window
- Queue length + scale-to-zero

---

## Next: Example configuration

Below is a **manual KEDA `ScaledObject` example** that:
- Replaces HPA
- Scales on CPU utilization
- Scales on GPU utilization via Prometheus
- Preserves familiar HPA scale-up behavior

You can apply it directly using `kubectl apply -f`.

```yaml
# -----------------------------
# (Optional) Secret for Prometheus auth (if you need it)
# If Prometheus is open inside the cluster, you can skip this entire section.
# -----------------------------
apiVersion: v1
kind: Secret
metadata:
  name: keda-prometheus-auth
  namespace: NAMESPACE
type: Opaque
stringData:
  bearerToken: "REPLACE_ME"   # or remove if not needed

---
# -----------------------------
# (Optional) TriggerAuthentication referencing the Secret above
# -----------------------------
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: prometheus-trigger-auth
  namespace: NAMESPACE
spec:
  secretTargetRef:
    - parameter: bearerToken
      name: keda-prometheus-auth
      key: bearerToken

---
# -----------------------------
# KEDA ScaledObject (the main object)
# This will create & manage an HPA for your Deployment.
# -----------------------------
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: prt-keda-modelhost-DEPLOYMENT_KEY
  namespace: NAMESPACE
spec:
  scaleTargetRef:
    name: prt-depl-modelhost-DEPLOYMENT_KEY

  # Similar semantics to HPA min/max
  minReplicaCount: 1
  maxReplicaCount: 10

  # How often KEDA polls triggers, and how long it waits before scaling down
  pollingInterval: 15        # seconds
  cooldownPeriod: 60         # seconds

  # (Optional) keep your familiar HPA behavior tuning
  advanced:
    horizontalPodAutoscalerConfig:
      behavior:
        scaleUp:
          stabilizationWindowSeconds: 60
          policies:
            - type: Pods
              value: 2
              periodSeconds: 30

  triggers:
    # 1) CPU utilization trigger (works like your HPA cpu averageUtilization)
    - type: cpu
      metricType: Utilization
      metadata:
        value: "75"

    # 2) GPU utilization via Prometheus scaler
    #
    # You MUST adjust the PromQL query to match your cluster's GPU metrics.
    # Common sources: DCGM exporter metrics scraped by Prometheus.
    #
    # This example expects the query returns a single number (0..100).
    - type: prometheus
      metadata:
        serverAddress: "http://prometheus-server.monitoring.svc.cluster.local:80"
        metricName: "gpu_utilization_percent"
        query: |
          avg(
            DCGM_FI_DEV_GPU_UTIL{namespace="NAMESPACE", pod=~"prt-depl-modelhost-DEPLOYMENT_KEY-.*"}
          )
        threshold: "70"
      # If you don't need auth, remove "authenticationRef".
      authenticationRef:
        name: prometheus-trigger-auth

```

## Scale from 0 with Istio (wake on incoming traffic)

When `minReplicaCount: 0`, **there are no Pods**, so your app cannot observe traffic or emit its own metrics.  
To scale from 0 → 1, you need a **demand signal that exists outside the Deployment**.

With Istio, there are two practical patterns:

---

### Option A (recommended for “no dropped requests”): HTTP request buffering in front of the service

Use a component that can **accept requests while the backend is at 0**, then trigger scale-up and **buffer** until at least 1 Pod is ready.

Typical approaches:
- **KEDA HTTP add-on** (interceptor/proxy in front of the service)
- Knative-style activator (if you already use Knative)

**Pros**
- Requests don’t immediately fail when replicas = 0
- Better UX for synchronous inference endpoints

**Cautions**
- Buffering is not free: you must cap queue size, max pending time, and timeouts
- Cold start can be long for GPU modelhost (image pull + model load)
- Decide what you want to happen under heavy burst (queue, shed load, 429, etc.)

---

### Option B (simple, but first requests may fail): scale on Istio/Ingress traffic metrics (Prometheus)

If you have Prometheus scraping Istio metrics, you can scale based on **request rate at the mesh / gateway layer** (which still exists when your pods are 0).

**Pros**
- No extra proxy/buffering component required
- Simple to operate if you already have Istio + Prometheus

**Cautions**
- When there are 0 endpoints, the first request(s) can return **503** until a Pod comes up
- You must rely on client retries, or Istio retries, to hide cold starts
- Prometheus scrape + KEDA polling add latency (not instant wake-up)

---

## YAML sample: KEDA scale-from-zero using Istio request rate (Prometheus)

> Adjust namespaces, gateway/workload labels, and the PromQL query to match your telemetry.
> This example assumes you scrape Istio metrics into Prometheus.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: prt-keda-modelhost-DEPLOYMENT_KEY
  namespace: NAMESPACE
spec:
  scaleTargetRef:
    name: prt-depl-modelhost-DEPLOYMENT_KEY

  # Allow scale-to-zero:
  minReplicaCount: 0
  maxReplicaCount: 10

  # Poll & cooldown are critical for traffic-based triggers
  pollingInterval: 15     # seconds
  cooldownPeriod: 120     # seconds (increase for GPU/model cold start)

  triggers:
    - type: prometheus
      metadata:
        serverAddress: "http://prometheus-server.monitoring.svc.cluster.local:80"
        metricName: "istio_rps_modelhost"
        # Example: requests per second to a service inside the mesh.
        # You may need different labels depending on your Istio telemetry setup.
        query: |
          sum(
            rate(istio_requests_total{
              destination_service_name="prt-svc-modelhost-DEPLOYMENT_KEY",
              destination_workload_namespace="NAMESPACE",
              response_code!~"5.."
            }[1m])
          )
        # Normal scaling threshold once active (RPS per replica-ish; tune to your service)
        threshold: "5"

        # Wake-up threshold from 0 (prevents noise waking pods)
        activationThreshold: "1"
```


---

**Previous**: [Trino API Guide](trino-api-guide.md) | **Next**: [Container Images](container-images.md)
