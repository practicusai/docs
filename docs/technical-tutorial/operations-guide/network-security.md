# Practicus AI Network Policies and Service-to-Service Traffic Control

This document describes how Practicus AI controls network traffic between internal services and modules using a layered approach:

- Layer 2 / Layer 3 / Layer 4 isolation with Kubernetes networking and NetworkPolicies
- Layer 7 control, encryption, and identity-aware authorization with Istio Service Mesh

Together, these mechanisms allow administrators to define, enforce, and manage strict network policies between all components of the Practicus AI platform, from data preparation and model training to large language model services and reporting dashboards.

## Layered Network Security Model

Practicus AI is typically deployed on Kubernetes, within a cloud or on-premises network that already enforces baseline security controls at the infrastructure level. On top of this, the platform adds progressively stricter controls:

1. **Infrastructure layer (L2/L3)**: VPCs, subnets, security groups, firewalls
2. **Kubernetes layer (L3/L4)**: NetworkPolicy objects for pod and namespace level isolation
3. **Service mesh layer (L7)**: Istio for mutual TLS (mTLS), service identity, and fine-grained authorization

This layered model enables both coarse-grained segmentation and fine-grained control over which Practicus AI services may communicate with each other, and under which conditions.

![Layered Network Security](img/network_sec_01_layered_network_security.svg)

## L2 / L3 / L4 Isolation With Kubernetes Network Policies

At the cluster level, Practicus AI relies on Kubernetes NetworkPolicies to define allowed flows between pods and namespaces. This covers Layer 3 and Layer 4 concerns such as IP, port, and protocol.

Typical patterns include:

- **Namespace based segmentation**: Each major Practicus AI module (for example data preparation, ML training, LLM serving, observability) can run in its own namespace. NetworkPolicies restrict which namespaces may initiate traffic to others.
- **Default deny, explicit allow**: For sensitive environments, the default policy can deny all ingress, and specific NetworkPolicies explicitly allow the minimal required communication flows.
- **Port and protocol scoping**: Policies specify which TCP/UDP ports are accessible, reducing the attack surface of each service.
- **Environment separation**: Development, test, and production clusters or namespaces can have different policy sets, while following the same conceptual model.

With L2/L3 plus Kubernetes NetworkPolicies, Practicus AI can implement scenarios such as:

- Only the model serving namespace is allowed to talk to the feature store namespace on the database port.
- Only the API gateway namespace is allowed to reach internal LLM services on HTTPS ports.
- Monitoring and observability components can scrape metrics endpoints but cannot access business data stores directly.

![Namespace segmentation](img/network_sec_02_namespace_segmentation.svg)

### Example: Default Deny and Allowed Ingress

The following example shows how a namespace can be configured with a default deny rule and a separate rule that allows ingress from a specific namespace.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: ml-platform
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-data-prep
  namespace: ml-platform
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              practicus-module: data-prep
      ports:
        - protocol: TCP
          port: 8080
```

In this example:

- The `ml-platform` namespace defaults to no ingress or egress.
- A second policy allows ingress to any pod in the `ml-platform` namespace on TCP port 8080, but only from namespaces labeled `practicus-module: data-prep`.

This is the foundational level of service-to-service network policy control in Practicus AI.

## Layer 7 Control With Istio Service Mesh (On Top of Kubernetes Policies)

Kubernetes NetworkPolicies are excellent for L3/L4 isolation, but they are not aware of higher level concepts such as HTTP paths, methods, or authenticated identities.

To add richer controls, Practicus AI can be deployed together with an Istio service mesh. Istio sidecar proxies intercept and secure traffic between services, enabling the following capabilities on top of existing Kubernetes policies:

- **Mutual TLS (mTLS)** for all service-to-service traffic
  - Each service has a strong cryptographic identity.
  - All internal traffic is encrypted in transit.
- **Identity-aware authorization** at Layer 7
  - Access decisions are based on service identity, namespace, service account, and request attributes.
- **Route-level control** via VirtualService and DestinationRule
  - Canaries, staged rollouts, retries, timeouts, and circuit breaking.
- **Centralized policy management** with AuthorizationPolicy resources
  - Policies are defined in a declarative way and kept under version control.

With Istio on top of Kubernetes policies, platform operators can express requirements such as:

- Only specific Practicus AI backend services may call an internal LLM endpoint, and only with certain methods and paths.
- Different roles (for example interactive notebooks vs batch jobs) are mapped to different service accounts, which in turn have distinct permissions enforced by AuthorizationPolicy resources.
- All inter-service traffic within the platform is encrypted and authenticated, even though services communicate over the internal cluster network.

![Istio L7](img/network_sec_03_istio_l7_auth.svg)

### End to end summary view

![End to end](img/network_sec_04_end_to_end.svg)

### Example: Istio AuthorizationPolicy for Internal APIs

The following example shows how Istio can restrict access to a service so that only callers from a specific namespace and service account are allowed.

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-ml-jobs-to-model-api
  namespace: model-serving
spec:
  selector:
    matchLabels:
      app: model-api
  action: ALLOW
  rules:
    - from:
        - source:
            namespaces: ["ml-jobs"]
            principals: ["cluster.local/ns/ml-jobs/sa/job-runner"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/v1/predict"]
```

Key points:

- The policy applies to pods labeled `app: model-api` in the `model-serving` namespace.
- It allows traffic only if the source is the `job-runner` service account in the `ml-jobs` namespace.
- It further restricts operations to HTTP POST requests on the `/v1/predict` path.

This is a Layer 7 network policy that builds on top of the network level isolation already enforced by Kubernetes NetworkPolicies and the cluster networking layer.

### Example: Istio VirtualService for Routing and Traffic Management

While AuthorizationPolicy governs who is allowed to access a service, Istio VirtualService and DestinationRule are used to control how traffic is routed to that service.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-api-routing
  namespace: model-serving
spec:
  hosts:
    - model-api
  http:
    - match:
        - uri:
            prefix: /v1/predict
      route:
        - destination:
            host: model-api
            subset: v2-canary
          weight: 10
        - destination:
            host: model-api
            subset: v1-stable
          weight: 90
      timeout: 5s
      retries:
        attempts: 2
        perTryTimeout: 2s
```

In this example, Istio:

- Splits traffic between two subsets of the same service (`v2-canary` and `v1-stable`).
- Provides retry and timeout behavior for requests to `/v1/predict`.

These routing controls complement the network policies by making it possible to manage rollout strategies and resilience without relaxing security boundaries.

## Combining Kubernetes Network Policies and Istio for Practicus AI

In a typical Practicus AI deployment:

- Each major functional area (data ingestion, data preparation, ML training, LLM serving, reporting, observability) is mapped to one or more Kubernetes namespaces.
- Kubernetes NetworkPolicies define which namespaces may talk to which, and on which ports.
- Istio provides mutual TLS, identity-aware authorization, and sophisticated routing on top of these base rules.

This combined approach offers the following benefits:

- **Strong segmentation**: L2/L3/L4 policies prevent unintended communication between components.
- **Fine-grained access control**: L7 policies lock down access to specific operations and paths.
- **Encrypted internal traffic**: mTLS ensures that even intra-cluster traffic is protected.
- **Operational flexibility**: Routing and rollout strategies can evolve without weakening access controls.
- **Compliance support**: Clear, declarative policies that can be audited and reviewed.

![Combined](img/network_sec_05_combined.svg)

## Policy Management, Versioning, and Operations

To ensure that network policies remain maintainable and auditable over time, Practicus AI deployments follow these operational best practices:

- **Infrastructure as code**
  - NetworkPolicy, AuthorizationPolicy, VirtualService, and related resources are defined as code (YAML) and stored in version control.
  - Changes are reviewed via standard code review processes.
- **GitOps or CI/CD based rollout**
  - Policies are applied to clusters via automated pipelines (for example Argo CD, Flux, or CI/CD jobs).
  - Rollbacks are straightforward if a policy misconfiguration is detected.
- **Monitoring and observability**
  - Metrics and logs from the service mesh and Kubernetes components expose policy enforcement behavior.
  - Dashboards can show which services are talking to which other services, and where denials or errors occur.
- **Environment specific baselines**
  - Development and test environments may use more permissive policies for rapid iteration.
  - Production environments use stricter default deny configurations with explicit allow lists.

This governance model makes it easier to maintain consistent and auditable network policies as the Practicus AI platform evolves.

## Summary

Practicus AI provides a robust and extensible approach to network policies and service-to-service traffic control by combining:

- L2/L3/L4 isolation and segmentation via Kubernetes cluster networking and NetworkPolicies
- L7 encryption, identity, and authorization via Istio service mesh
- Declarative, version controlled policy definitions and automated rollout processes

This layered design enables organizations to define and manage strict network policies across all Practicus AI components, while preserving flexibility for future growth and architectural changes.


---

**Previous**: [MFA](mfa.md) | **Next**: [How To > Automate Notebooks > Executing Notebooks](../how-to/automate-notebooks/executing-notebooks.md)
