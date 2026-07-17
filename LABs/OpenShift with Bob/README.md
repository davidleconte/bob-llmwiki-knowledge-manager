# Learning and Exploring OpenShift with Bob
Welcome to a hands-on exploration of OpenShift operations using IBM Bob's AI-native approach. This learning path guides you through managing cloud-native applications using natural language, building both technical skills and conceptual understanding of container orchestration.

## Lab Overview

OpenShift runs applications on Kubernetes using a **declarative model**. You define the desired state of an application, and the platform continuously works to make the cluster match it.

In this lab, you will deploy a simple application and observe **how the system responds behind the scenes**. You will inspect key resources such as **Deployments, ReplicaSets, Pods, Services, and Routes**, and see how they work together to run and expose workloads.

You will also explore how the **scheduler places pods on nodes**, how **services enable networking**, and how OpenShift maintains **stability through resource and security policies**.

The goal is simple: build a **clear mental model of how OpenShift actually operates** — not just how to run commands.

## Prerequisites

- Access to an OpenShift cluster (ROKS, CRC, or any OpenShift 4.x - e.g. a TechZone cluster) and a namespace/project for experimentation
- `oc` CLI installed and authenticated
- IBM Bob (Antigravity IDE) installed
- The `application-samples` directory from this repository

## Getting Started

### 1. Verify Your Environment

Ensure you can connect to your OpenShift cluster:

```bash
oc login <cluster-url> --token=<your-token>
oc whoami
oc new-project <your-namespace>
# if your test namespace exists already
oc project <your-namespace>
```

### 2. Add a custom OpenShift mode to Bob

Follow the [Bob documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes) to add a custom OpenShift DevOps mode based on [this yaml file](./resources/openshift-devops.yaml):

Click the icon in the Bob panel to open Settings.

Select the `Modes` tab.

Click the button to create a new mode and add the contents of the yaml file provided.

Use the **🚢🛡️ OpenShift DevOps** mode for this lab.


### 3. Begin Your Learning Journey

Start with [Part 1 - OpenShift 101 with Bob](./WORKSHOP-openshift-part1.md) and progress at your own pace. Each section builds on previous concepts, but you can revisit earlier material as needed.
Running into issues? Dive into [Part 2 – Observability & Troubleshooting](./WORKSHOP-openshift-part2.md).

**Ready to begin?** Open the [lab](./WORKSHOP-openshift-part1.md) and start your learning journey!🚀

