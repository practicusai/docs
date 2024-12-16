---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Advanced GPU Resource Management with Practicus AI

This document provides an overview of how to configure partial NVIDIA GPUs (MIG), along with high-level steps for AMD and Intel GPU support, and how Practicus AI platform facilitates GPU management.

### Topics covered in this document
- Partial NVIDIA GPUs (MIG)
- AMD GPUs
- Intel GPUs

---

## 1. **Partial NVIDIA GPUs (MIG)**

### **How MIG Works**
- NVIDIA's `Multi-Instance GPU (MIG)` feature allows you to split a single physical GPU (e.g., NVIDIA A100m, H100, H200) into multiple independent GPU instances.
- Each MIG instance provides dedicated memory and compute resources, ideal for running multiple workloads on the same GPU.

### **Setup Steps**
1. **Enable MIG Mode on the GPU**:
   - Log into the GPU node and enable MIG using `nvidia-smi`:
     ```bash
     sudo nvidia-smi -i 0 --mig-enable
     sudo reboot
     ```
   - After reboot, confirm MIG mode is enabled:
     ```bash
     nvidia-smi
     ```

2. **Create MIG Instances**:
   - Use `nvidia-smi` to create MIG profiles. For example, split a GPU into 7 instances:
     ```bash
     sudo nvidia-smi mig -i 0 -cgi 0,1,2,3,4,5,6
     sudo nvidia-smi mig -i 0 -cci
     ```
   - Check the configuration:
     ```bash
     nvidia-smi
     ```

3. **Expose MIG Resources in Kubernetes**:
   - Deploy the NVIDIA Device Plugin:
     ```bash
     kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/deployments/k8s-device-plugin-daemonset.yaml
     ```
   - Verify available resources:
     ```bash
     kubectl describe node <node-name>
     ```

- To learn more please visit:
    - https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-operator-mig.html

---

## 2. **Custom GPU Configuration in Practicus AI**

Practicus AI simplifies advanced GPU management through the intuitive management UI:

**Open Practicus AI Management Console**:
- Access the platform's web console for infrustructure management.

**Select Worker Sizes**:
- Choose from predefined worker sizes or create a new one to include GPU capacity :
   - `Number of GPUs`
   - `Amount of Video RAM (VRAM)`

**Enter GPU Type Selector**:
- Specify the custom GPU type you need:
    - Specify for Nvidia MIG (e.g. `nvidia.com/mig-1g.5gb`) you defined in the above step.
    - Specify for other vendors (e.g., `amd.com/gpu` or `intel.com/gpu`).
    - Leave empty for the default, which will use entire NVDIA GPUs without fractions.

**Deploy workloads as usual**:
- Deploy end user workers, model hosts, app hosts etc. as usual with the worker size you defined above.
- The platform will dynamically manage the resources with the selected GPU configuration.

**Example Configuration**

- If you set GPU count to 2, with a GPU type selector of `nvidia.com/mig-1g.5gb` running on a single ``NVIDIA H100 GPU``, the end user could get **two separate GPU instances**, each with **1/7th of the GPU's compute and memory resources (1 compute slice and 5 GB of memory per instance)**.
- This configuration allows the same physical GPU to handle multiple workloads independently, providing dedicated resources for each workload without interference. 
- This setup is ideal for lightweight GPU workloads, such as inference or smaller-scale training tasks, that do not require the full power of an entire GPU.

**Important Note**  
- Please note that the VRAM setting in the **Practicus AI Management Console** does **not** dictate how much VRAM a user gets. It is only used to **measure usage** and ensure a user is kept within their designated daily/weekly/monthly usage limits. 
- To actually **enforce VRAM limits**, you must use **NVIDIA MIG profiles** (e.g., `nvidia.com/mig-1g.5gb`) or equivalent to `apply resource constraints at the hardware level.`

---

## 3. **High-Level Steps for AMD GPUs**

AMD GPUs (e.g., using ROCm) require setup similar to NVIDIA but with their own tools and configurations:

1. **Install AMD ROCm Drivers**:
   - Install ROCm drivers on the nodes with AMD GPUs.

2. **Deploy AMD Device Plugin**:
   - Use the AMD ROCm Kubernetes device plugin to expose AMD GPU resources:
     ```bash
     kubectl apply -f https://github.com/RadeonOpenCompute/k8s-device-plugin
     ```

The rest is the same as NVIDIA MIG, define a new worker size and use the GPU Type Selector `amd.com/gpu`

---

## 4. **High-Level Steps for Intel GPUs**

Intel GPUs can be managed using the Intel GPU Device Plugin:

1. **Install Intel GPU Drivers**:
   - Install Intel drivers and libraries for iGPU or discrete GPU support.

2. **Deploy Intel Device Plugin**:
   - Use the Intel GPU plugin to expose GPU resources:
     ```bash
     kubectl apply -f https://github.com/intel/intel-device-plugins-for-kubernetes
     ```
The rest is the same as NVIDIA MIG, define a new worker size and use the GPU Type Selector `intel.com/gpu`


---

**Previous**: [Customize Templates](customize-templates.md) | **Next**: [Configure Workspaces](configure-workspaces.md)
