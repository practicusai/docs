# Practicus AI Operations Tutorial

In this demo we will focus on the **operational** side of Practicus AI. This tutorial will guide you through how to manage, monitor, and maintain the platform in production at scale. Whether you're running Practicus AI on a public cloud Kubernetes environment such as AWS EKS, Azure AKS, Google GKE, or on-premises solutions like Red Hat OpenShift or Rancher, understanding these operational best practices ensures a stable, scalable system.

## Overview

- **Cloud-Native & On-Prem Flexibility**  
  Practicus AI is fully cloud-native and can be deployed across various Kubernetes-based environments—from major cloud providers to on-premises clusters. 

- **Observability & Monitoring**  
  Ability to track logs, metrics, events, and errors across your Practicus AI deployments. By leveraging add-on services like Grafana, you can create real-time dashboards and alerts to ensure continuous uptime and optimal performance.

- **Workflow & Scheduling**  
  Airflow integration provides a robust solution for scheduling and automating complex data pipelines. In an enterprise setting, these workflows often involve cross-team or cross-department coordination—this tutorial shows you how to manage and monitor such tasks seamlessly.

- **Security & Compliance**  
  As part of day-2 operations, you’ll need to ensure that your deployments adhere to security best practices. This includes understanding Kubernetes namespace isolation, role-based access control (RBAC), and any compliance measures your organization must meet.

---

[Next >](create-user-group.md)