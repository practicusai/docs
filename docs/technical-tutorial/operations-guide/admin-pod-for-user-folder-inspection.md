# Kubernetes Pod Definition: Admin Access for User Folder Inspection

## Description

In the Practicus platform, there are situations where administrators need to inspect users' `/my` folders, which are automatically mounted via PVs/PVCs. This document aims to provide a Kubernetes Pod definition that allows administrators to mount a specified user's `/my` folder into their own pod to perform this inspection.

## Solution

The following YAML definition allows an administrator to mount `{{TARGET_USERNAME}}`'s personal folder into their pod at `/home/ubuntu/{{TARGET_USERNAME}}`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  # Pod name for the admin viewer pod. Replace {{TARGET_USERNAME}} with the actual username.
  name: prt-pod-user-folder-viewer-{{TARGET_USERNAME}}
  namespace: prt-ns
spec:
  restartPolicy: Never
  volumes:
    # Volume definition for mounting the target user's Persistent Volume Claim (PVC).
    # Replace {{TARGET_USERNAME}} with the actual username.
    - name: prt-vol-user-folder-viewer-{{TARGET_USERNAME}}
      persistentVolumeClaim:
        # Claim name for the target user's PVC. Replace {{TARGET_USERNAME}} with the actual username.
        claimName: prt-pvc-my-{{TARGET_USERNAME}}
  containers:
    - name: ubuntu
      image: ubuntu:22.04
      command: ["/bin/bash", "-c", "sleep infinity"] 
      volumeMounts:
        # Mount the volume defined above. Replace {{TARGET_USERNAME}} with the actual username.
        - name: prt-vol-user-folder-viewer-{{TARGET_USERNAME}}
          # Mount path inside the pod where the user's folder will be accessible.
          # Replace {{TARGET_USERNAME}} with the actual username.
          mountPath: /home/ubuntu/{{TARGET_USERNAME}}
```

## Usage Instructions

1.  Save the YAML content above to a file (e.g., `admin-viewer-pod.yaml`).
2.  Replace the placeholders `{{TARGET_USERNAME}}` within the YAML with the actual username of the user you wish to inspect.
3.  To deploy the pod to your Kubernetes cluster:
    ```bash
    kubectl apply -f admin-viewer-pod.yaml -n prt-ns
    # or if you are using OpenShift:
    oc apply -f admin-viewer-pod.yaml -n prt-ns
    ```
4.  Once the pod is ready, you can exec into it to inspect the user's folder:
    ```bash
    kubectl exec -it prt-pod-user-folder-viewer-{{TARGET_USERNAME}} -n prt-ns -- bash
    # or if you are using OpenShift:
    oc exec -it prt-pod-user-folder-viewer-{{TARGET_USERNAME}} -n prt-ns -- bash
    ```
5.  Inside the pod, navigate to the folder using `cd /home/ubuntu/{{TARGET_USERNAME}}`.
6.  Remember to delete the pod when you are finished:
    ```bash
    kubectl delete pod prt-pod-user-folder-viewer-{{TARGET_USERNAME}} -n prt-ns
    # or if you are using OpenShift:
    oc delete pod prt-pod-user-folder-viewer-{{TARGET_USERNAME}} -n prt-ns
    ```

## Note

This pod has a minimal configuration. You may need to customize fields such as `image`, `resources`, `securityContext`, etc., according to your environment's security and resource requirements.

---

**Previous**: [Network Security](network-security.md) | **Next**: [Automating Kerberos Ticket Renewal With Cron](automating-kerberos-ticket-renewal-with-cron.md)
