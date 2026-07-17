# OpenShift 101 with Bob

## Learning Objectives

By the end of this lab, you will understand:

1. **The Control Loop Architecture** - How OpenShift continuously reconciles desired state with actual state
2. **The Resource Hierarchy** - Why Deployments create ReplicaSets which create Pods, and what each layer provides
3. **Service Discovery & Load Balancing** - How Services provide stable endpoints and Routes expose them externally
4. **The Scheduler's Decision Process** - What factors determine where pods run
5. **Security Boundaries** - How SCCs, RBAC, and namespaces create isolation
6. **Resource Governance** - How quotas and limits prevent resource exhaustion

💡 If something doesn’t work as expected, check out [Part 2 – Observability & Troubleshooting](./WORKSHOP-openshift-part2.md).

---

## Step 1 – Discover the Cluster Topology

### Why This Matters

Before deploying anything, you need to understand the cluster's structure. OpenShift is a distributed system with control plane nodes (managing state) and worker nodes (running workloads). Your operations exist within this topology, and understanding it helps you reason about scheduling, networking, and failure domains.

### Prompt

```
Connect to my OpenShift cluster and show me its topology. I want to understand:
- What nodes exist and their roles
- What namespaces are available
- What my current project is
- What resources already exist in my namespace
```

### What to Observe

Bob should execute commands like:
- `oc whoami` - Verify authentication
- `oc get nodes` - Show cluster nodes and their roles (control-plane vs worker)
- `oc get projects` or `oc projects` - List available namespaces
- `oc project` - Show current namespace
- `oc describe project <your-namespace>` - Describe the resources in your test namespace

Watch for:
- Node count and capacity (CPU, memory)
- Namespace isolation boundaries
- Whether your namespace is empty or has existing workloads

### Checkpoint

- ✅ Authenticated to cluster
- ✅ Can see node topology (control plane + workers)
- ✅ Current namespace identified
- ✅ Resource inventory complete

### Reflection

1. **Why separate control plane and worker nodes?** What happens if a worker fails vs. if the control plane fails?
2. **What is a namespace really?** Is it just a naming boundary, or does it provide other isolation?
3. **What resources exist even in an "empty" namespace?** (Hint: service accounts, default secrets)

Understanding topology is foundational—every operation you perform happens within this distributed system.

---

## Step 2 – Deploy Your First Workload and Understand the Resource Hierarchy

### Why This Matters

When you deploy an application, you're not directly creating containers. You're declaring desired state to the control plane, which then orchestrates a hierarchy of resources: Deployment → ReplicaSet → Pod → Container. Each layer serves a purpose. Understanding this hierarchy is critical to debugging, scaling, and operating workloads.

### Prompt

```
Deploy the helloworld application from application-samples/helloworld/deployment.yaml.
After deploying, explain the resource hierarchy that was created:
- What is the Deployment?
- What ReplicaSet was created and why?
- What Pods exist and what's their relationship to the ReplicaSet?
- Show me the events that occurred during deployment.
```

### What to Observe

Bob should:
1. Read [`application-samples/helloworld/deployment.yaml`](application-samples/helloworld/deployment.yaml)
2. Apply it with `oc apply -f`
3. Show the created resources:
   - `oc get deployment` - The desired state declaration
   - `oc get replicaset` - The controller managing pod replicas
   - `oc get pods` - The actual running containers
4. Display events: `oc get events --sort-by='.lastTimestamp'`

Watch for:
- The Deployment creates a ReplicaSet (with a generated hash suffix)
- The ReplicaSet creates Pod(s) matching the replica count
- Events showing: Scheduled → Pulling → Pulled → Created → Started

### Checkpoint

- ✅ Deployment exists with desired replica count
- ✅ ReplicaSet created by Deployment
- ✅ Pod(s) in Running state
- ✅ Events show successful scheduling and container startup

### Reflection

1. **Why the three-layer hierarchy?** Why not just create Pods directly?
   - *Hint: What happens when you update the image? When a pod crashes? When you scale?*

2. **What is the ReplicaSet's job?** Why does the Deployment create it instead of creating Pods directly?
   - *Hint: Think about rolling updates and rollback*

3. **What does "desired state" mean?** If you delete a Pod, what happens and why?
   - *Hint: Try it—delete a pod and watch what happens*

The Deployment is your *intent*. The ReplicaSet is the *reconciliation controller*. The Pod is the *actual workload*. This separation enables self-healing and declarative updates.

---

## Step 3 – Expose the Application with a Service (Understanding Service Discovery)

### Why This Matters

Pods are ephemeral—they get IP addresses that change when they restart. Services provide stable endpoints that automatically load-balance across healthy pods. This is fundamental to how microservices communicate in Kubernetes.

### Prompt

```
Create a Service to expose the helloworld deployment internally on port 8080.
Then explain:
- How does the Service find the Pods?
- What happens if a Pod restarts and gets a new IP?
- Show me the Service's endpoints and how they map to Pods.
```

### What to Observe

Bob should:
1. Create a service with `oc expose deployment hello --port=8080 --target-port=8080 --name=hello-service`
2. Show endpoints: `oc get endpoints helloworld-app-svc` or `oc get services` to show all services in the namespace
3. Explain the selector mechanism

Watch for:
- The Service has a stable ClusterIP
- Endpoints list shows Pod IPs and ports
- The selector matches Pod labels

### Checkpoint

- ✅ Service created with ClusterIP
- ✅ Service selector matches Pod labels
- ✅ Endpoints show Pod IPs
- ✅ Service port maps to container port

### Reflection

1. **How does the Service "find" Pods?** What's the mechanism?
   - *Hint: Look at the Service's `selector` and the Pod's `labels`*

2. **What happens when you scale to 3 replicas?** How do the endpoints change?
   - *Try it: Scale the deployment and watch the endpoints*

3. **What is a ClusterIP?** Why is it stable when Pod IPs change?
   - *Hint: Think about DNS and kube-proxy*

Services are the foundation of service discovery. They decouple consumers from providers, enabling dynamic scaling and self-healing.

---

## Step 4 – Expose Externally with a Route (Understanding Ingress)

### Why This Matters

Services provide internal connectivity, but external users need a way in. OpenShift Routes (built on HAProxy) provide HTTP/HTTPS ingress with TLS termination, load balancing, and hostname-based routing. Understanding Routes helps you design external access patterns.

### Prompt

```
Create an OpenShift Route to expose the helloworld service externally.
Then explain:
- How does the Route connect to the Service?
- What is the router doing behind the scenes?
- Show me the full request path: External User → Route → Service → Pod
Test the route with curl to verify it's working.
```

### What to Observe

Bob should:
1. Create a route `oc expose service hello-service --name=hello-route`
2. Show the Route: `oc get route hello-route` or `oc get routes` to show all routes in the namespace
3. Test it: `curl <route-url>`
4. Explain the request flow

Watch for:
- The Route has a hostname (usually `<app>-<namespace>.<cluster-domain>`)
- The Route targets the Service by name
- The Service load-balances to Pod endpoints
- The curl response shows the application is accessible

### Checkpoint

- ✅ Route created with external hostname
- ✅ Route targets the Service
- ✅ HTTP request succeeds
- ✅ Response comes from the application

### Reflection

1. **What is the OpenShift router?** Where does it run and how does it know about your Route?
   - *Hint: It's a pod running HAProxy, watching Route resources*

2. **What happens if you have 3 pods?** How does traffic get distributed?
   - *Hint: The router load-balances to the Service, which load-balances to Pods*

3. **What's the difference between a Route and an Ingress?** Why does OpenShift have both?
   - *Hint: Routes predate Kubernetes Ingress and offer more features*

The request path is: **External User → Router (HAProxy) → Service (kube-proxy) → Pod (container)**. Each layer provides load balancing and health checking.

---

## Step 5 – Scale Manually and Understand the Reconciliation Loop

### Why This Matters

Scaling reveals how OpenShift's control loop works. When you change desired state (replica count), controllers detect the drift and reconcile actual state to match. This is the heart of Kubernetes—continuous reconciliation toward desired state.

### Prompt

```
Scale the helloworld deployment to 3 replicas.
While it's scaling, explain what's happening:
- What controller detects the change?
- What steps does it take to reconcile?
- Show me the events and pod creation in real-time.
- What happens if I delete a pod after scaling?
```

### What to Observe

Bob should:
1. Scale: `oc scale deployment hello --replicas=3`
2. Watch in real-time: `oc get pods -w` (or show events)
3. Explain the reconciliation loop:
   - Deployment controller updates ReplicaSet
   - ReplicaSet controller creates new Pods
   - Scheduler assigns Pods to nodes
   - Kubelet starts containers
4. Delete a pod: `oc delete pod <pod-name>`
5. Show it gets recreated immediately

Watch for:
- New pods appearing with Pending → ContainerCreating → Running states
- Events showing scheduling and container startup
- Deleted pod being replaced automatically

### Checkpoint

- ✅ Deployment scaled to 3 replicas
- ✅ All 3 pods running
- ✅ Service endpoints updated to include all 3 pods
- ✅ Deleted pod automatically replaced

### Reflection

1. **What is the reconciliation loop?** How often does it run?
   - *Hint: Controllers continuously watch for drift between desired and actual state*

2. **Why does deleting a pod cause it to be recreated?** What component is responsible?
   - *Hint: The ReplicaSet controller maintains the desired replica count*

3. **What would happen if you deleted the ReplicaSet?** Would the pods survive?
   - *Hint: Try it—the Deployment controller will recreate the ReplicaSet*

This is declarative infrastructure: you declare *what* you want, and controllers continuously ensure *it stays that way*.

---

## Step 6 – Implement Autoscaling with HPA (Understanding Metrics-Driven Scaling)

### Why This Matters

Manual scaling is reactive. Horizontal Pod Autoscaler (HPA) enables proactive, metrics-driven scaling. But HPA requires resource requests to calculate utilization percentages. This step reveals how resource management and autoscaling interact.

### Prompt

```
Configure Horizontal Pod Autoscaler for the helloworld deployment:
- Scale between 2 and 5 replicas
- Target 70% CPU utilization
- First, update the deployment to set CPU requests to 100m and limits to 200m

Explain:
- Why does HPA need resource requests?
- How does it calculate "70% CPU utilization"?
- What happens if CPU exceeds the target?
```

### What to Observe

Bob should:
1. Update the deployment: `oc set resources deployment hello --requests=cpu=100m --limits=cpu=200m`
2. Create HPA: `oc autoscale deployment hello --min=2 --max=5 --cpu-percent=70`
3. Show HPA status: `oc get hpa`
4. Explain the calculation: 70% of 100m request = 70m per pod

Watch for:
- HPA showing current CPU utilization (may be "unknown" initially)
- Current vs desired replica count
- HPA adjusting replicas based on metrics

### Checkpoint

- ✅ Deployment has resource requests and limits
- ✅ HPA created with min=2, max=5
- ✅ HPA shows current metrics
- ✅ Replica count adjusts based on load (if load exists)

### Reflection

1. **Why are resource requests required for HPA?** What would "70% CPU" mean without them?
   - *Hint: 70% of what? Requests define the baseline*

2. **What's the difference between requests and limits?**
   - *Hint: Requests affect scheduling; limits affect runtime enforcement*

3. **How does HPA get metrics?** What component provides CPU/memory data?
   - *Hint: The metrics-server collects data from kubelets*

HPA is a controller that watches metrics and adjusts replica count. It's another reconciliation loop, but driven by observability data instead of manual changes.

---

## Step 7 – Implement Resource Quotas (Understanding Multi-Tenancy)

### Why This Matters

In multi-tenant clusters, namespaces share physical resources. Without governance, one namespace can starve others. ResourceQuotas and LimitRanges enforce boundaries, ensuring fair sharing and preventing resource exhaustion.

### Prompt

```
Implement resource governance for this namespace:
1. Create a ResourceQuota limiting:
   - Total CPU: 2 cores
   - Total memory: 4Gi
   - Max pods: 10

2. Create a LimitRange setting defaults for pods without resource specs:
   - Default CPU request: 100m
   - Default memory request: 128Mi
   - Default CPU limit: 500m
   - Default memory limit: 512Mi

Show me the current quota usage and explain what happens if I try to exceed it.
```

### What to Observe

Bob should:
1. Create ResourceQuota and LimitRange using `oc create`
2. Show quota and limit status using `oc describe`
4. Show current usage vs limits
5. Explain enforcement: new pods are rejected if quota would be exceeded

Watch for:
- Quota showing used vs hard limits
- LimitRange providing defaults for pods without resource specs
- Quota preventing over-allocation

### Checkpoint

- ✅ ResourceQuota created and enforced
- ✅ LimitRange created with defaults
- ✅ Current usage displayed
- ✅ Quota prevents exceeding limits

### Reflection

1. **Why separate ResourceQuota and LimitRange?** What does each control?
   - *Hint: Quota limits the namespace total; LimitRange sets per-pod defaults and constraints*

2. **What happens if you try to create a pod that would exceed the quota?**
   - *Hint: The admission controller rejects it before it's created*

3. **How do quotas enable multi-tenancy?** What would happen without them?
   - *Hint: One namespace could consume all cluster resources*

Quotas are admission controls—they enforce policy at creation time, preventing resource exhaustion before it happens.

---

## Step 8 – Configure Security Context Constraints (Understanding OpenShift Security)

### Why This Matters

OpenShift's Security Context Constraints (SCCs) are more restrictive than standard Kubernetes. By default, containers cannot run as root, cannot access the host, and have minimal capabilities. This step shows how to diagnose SCC violations and configure workloads to run securely.

### Prompt

```
Let's explore OpenShift security:
1. First, show me what SCCs exist in the cluster
2. Update the helloworld deployment to try running as root (UID 0) with privileged access
3. Watch it fail and explain why
4. Fix it by configuring a proper security context that:
   - Runs as non-root
   - Drops all capabilities
   - Disables privilege escalation
   - Uses a read-only root filesystem where possible

Explain what each security setting prevents.
```

### What to Observe

Bob should:
1. List SCCs: `oc get scc`
2. Update deployment to violate SCC (run as root, privileged)
3. Show pod failure: `oc describe pod` (look for SCC violation events)
4. Fix with proper securityContext:
   ```yaml
   securityContext:
     runAsNonRoot: true
     allowPrivilegeEscalation: false
     capabilities:
       drop:
         - ALL
     seccompProfile:
       type: RuntimeDefault
   ```
5. Verify pod starts successfully

Watch for:
- Pod stuck in CreateContainerConfigError or similar
- Events showing SCC violation
- After fix, pod runs with restricted SCC

### Checkpoint

- ✅ SCC violation identified and explained
- ✅ Proper security context configured
- ✅ Pod runs with restricted SCC
- ✅ Application functions correctly with security constraints

### Reflection

1. **Why does OpenShift default to restrictive SCCs?** What attacks does this prevent?
   - *Hint: Running as root enables container escape and host compromise*

2. **What are capabilities?** Why drop them all?
   - *Hint: Linux capabilities grant specific privileges (e.g., CAP_NET_ADMIN, CAP_SYS_ADMIN)*

3. **When would you need a less restrictive SCC?** How would you justify it?
   - *Hint: Some workloads (e.g., monitoring agents) need host access, but require security review*

SCCs are OpenShift's security model. They enforce least-privilege by default, requiring explicit justification for elevated permissions.

---

## Step 9 – Manage Secrets Securely (Understanding Secret Lifecycle)

### Why This Matters

Applications need credentials, API keys, and certificates. Secrets provide a way to inject sensitive data without hardcoding it. But secrets are only base64-encoded by default—understanding their limitations and best practices is critical for production security.

### Prompt

```
The hello application needs database credentials.
1. Create a Secret named 'app-database-credentials' with:
   - username: appuser
   - password: SecureP@ssw0rd123
   - database: helloworld_db

2. Update the deployment to inject these as environment variables:
   - DB_USER from username
   - DB_PASSWORD from password
   - DB_NAME from database

3. Verify the secret is available in the pod WITHOUT exposing the values in logs

4. Explain:
   - How are secrets stored in etcd?
   - What are the security limitations?
   - What would you do differently in production?
```

### What to Observe

Bob should:
1. Create secret: `oc create secret generic app-database-credentials \
  --from-literal=username=appuser \
  --from-literal=password='SecureP@ssw0rd123' \
  --from-literal=database=helloworld_db`
2. Update deployment to reference secret as env vars
3. Verify: `oc exec <pod> -- env | grep DB_` (but warn about exposing secrets)
4. Explain:
   - Secrets are base64-encoded, not encrypted (unless etcd encryption is enabled)
   - RBAC controls access
   - Production should use external secret managers (Vault, External Secrets Operator)

Watch for:
- Secret created successfully
- Deployment references secret
- Environment variables available in pod
- Bob warning about secret exposure risks

### Checkpoint

- ✅ Secret created
- ✅ Deployment references secret
- ✅ Environment variables available in pod
- ✅ Secret values not exposed in logs or output

### Reflection

1. **Are Kubernetes Secrets actually secure?** What are their limitations?
   - *Hint: Base64 is encoding, not encryption. Anyone with namespace access can read them*

2. **What's the difference between environment variables and volume mounts for secrets?**
   - *Hint: Env vars are visible in `ps` and logs; volumes can be updated without pod restart*

3. **How would you rotate secrets in production?** What's the process?
   - *Hint: Update secret, restart pods, or use external secret managers with automatic rotation*

Secrets are better than hardcoding, but they're not a complete security solution. Production requires external secret management, encryption at rest, and rotation policies.

---

## Step 10 – Implement RBAC (Understanding Authorization)

### Why This Matters

OpenShift is multi-user and multi-tenant. RBAC (Role-Based Access Control) defines who can do what. Understanding Roles, RoleBindings, ServiceAccounts, and the principle of least privilege is essential for secure operations.

### Prompt

```
Configure RBAC for this namespace:
1. Create a ServiceAccount named 'app-deployer' for CI/CD automation
2. Create a custom Role named 'pod-reader' that allows:
   - Getting, listing, and watching pods
   - Getting pod logs
   - NO permission to create, update, or delete pods
3. Create a RoleBinding granting 'pod-reader' to a user named 'developer1'
4. Create another RoleBinding granting 'edit' permissions to the 'app-deployer' ServiceAccount
5. Test permissions using 'oc auth can-i'

Explain the difference between Roles and ClusterRoles, and when to use each.
```

### What to Observe

Bob should:
1. Create ServiceAccount: `oc create serviceaccount app-deployer`
2. Create a custom and Role RoleBindings 
3. Test permissions for `developer1` and `app-deployer`, for example:
   ```bash
   oc auth can-i get pods --as=developer1
   oc auth can-i delete pods --as=developer1
   oc auth can-i create deployments --as=system:serviceaccount:<namespace>:app-deployer
   ```
5. Explain RBAC components and scope

Watch for:
- ServiceAccount created with auto-generated token secret
- Role with specific verbs and resources
- RoleBindings connecting subjects to roles
- Permission tests showing allowed/denied actions

### Checkpoint

- ✅ ServiceAccount created
- ✅ Custom Role created with specific permissions
- ✅ RoleBindings created for user and ServiceAccount
- ✅ Permissions tested and verified

### Reflection

1. **What's the difference between a Role and a ClusterRole?**
   - *Hint: Roles are namespace-scoped; ClusterRoles are cluster-wide*

2. **Why use ServiceAccounts instead of user credentials for automation?**
   - *Hint: ServiceAccounts are scoped, auditable, and don't require user passwords*

3. **What is the principle of least privilege?** How does RBAC enforce it?
   - *Hint: Grant only the minimum permissions needed; RBAC makes this explicit and auditable*

RBAC is how OpenShift enforces authorization. Every API request is checked against RBAC policies before being allowed.

---

## Step 11 – Understand Pod Scheduling (Understanding the Scheduler)

### Why This Matters

The scheduler decides where pods run. It considers resource requests, node capacity, affinity rules, taints/tolerations, and topology constraints. Understanding scheduling helps you design workloads that distribute properly and handle failures gracefully.

### Prompt

```
Explain how pod scheduling works in OpenShift.

Use `oc get pods -o wide` only as a reference point. Do not execute commands.

Focus on:
- how to interpret pod-to-node mapping
- how the scheduler makes decisions (resources, distribution, constraints)
- what patterns reveal scheduling behavior

Explain what happens and why — not how to run it.
```

### What to Observe

Bob should:
1. Show pod placement: `oc get pods -o wide`
2. Explain scheduling factors based on resource requests vs node capacity and the existing pod distribution and examples

Watch for:
- Pods distributed across nodes (if multiple nodes exist)
- Affinity rules influencing placement
- Scheduler events in pod descriptions

### Checkpoint

- ✅ Pod placement visible across nodes
- ✅ Affinity rules configured
- ✅ Anti-affinity spreads pods across nodes
- ✅ Scheduling behavior explained

### Reflection

1. **What's the difference between required and preferred affinity?**
   - *Hint: Required blocks scheduling if not satisfied; preferred is a soft constraint*

2. **Why spread pods across nodes?** What failure scenario does this address?
   - *Hint: If all pods are on one node and it fails, the entire application goes down*

3. **What are taints and tolerations?** How do they differ from affinity?
   - *Hint: Taints repel pods; tolerations allow pods to tolerate taints*

The scheduler is a sophisticated placement engine. Understanding it helps you design resilient, well-distributed workloads.

---

## Final Architecture

You've built a complete OpenShift application with production-ready patterns:

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenShift Cluster                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Your Namespace                           │  │
│  │                                                       │  │
│  │  External User                                        │  │
│  │       │                                               │  │
│  │       ▼                                               │  │
│  │  ┌─────────┐                                          │  │
│  │  │  Route  │ (HAProxy Router)                        │  │
│  │  │ (HTTPS) │                                          │  │
│  │  └────┬────┘                                          │  │
│  │       │                                               │  │
│  │       ▼                                               │  │
│  │  ┌──────────┐                                         │  │
│  │  │ Service  │ (ClusterIP, Load Balancer)             │  │
│  │  │  :8080   │                                         │  │
│  │  └────┬─────┘                                         │  │
│  │       │                                               │  │
│  │  ┌────┴────┬────────┐                                │  │
│  │  ▼         ▼        ▼                                │  │
│  │ ┌───┐    ┌───┐    ┌───┐                             │  │
│  │ │Pod│    │Pod│    │Pod│ (Containers)                │  │
│  │ └─┬─┘    └─┬─┘    └─┬─┘                             │  │
│  │   │        │        │                                │  │
│  │   └────────┴────────┘                                │  │
│  │            │                                          │  │
│  │            ▼                                          │  │
│  │       ┌─────────┐                                    │  │
│  │       │ Secret  │ (DB Credentials)                   │  │
│  │       └─────────┘                                    │  │
│  │                                                       │  │
│  │  Controllers:                                         │  │
│  │  • Deployment Controller (manages ReplicaSets)       │  │
│  │  • ReplicaSet Controller (maintains pod count)       │  │
│  │  • HPA Controller (scales based on metrics)          │  │
│  │  • Scheduler (places pods on nodes)                  │  │
│  │                                                       │  │
│  │  Governance:                                          │  │
│  │  • ResourceQuota (2 CPU, 4Gi RAM, 10 pods)          │  │
│  │  • LimitRange (default requests/limits)              │  │
│  │  • SCC (restricted security context)                 │  │
│  │  • RBAC (roles, rolebindings, service accounts)      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```
---

## Additional Resources

- [OpenShift Documentation](https://docs.redhat.com/en/documentation/openshift_container_platform/latest/)
- [OpenShift Overview](https://developers.redhat.com/products/openshift/overview)
- [Free, interactive tutorials for learning OpenShift (Katacoda)](https://developers.redhat.com/products/openshift)
- Relevant courses from the Red Hat Partner Portal include:
    - OCP Installation: Red Hat OpenShift Installation Lab (DO322)
    - OCP Administration basic: Red Hat OpenShift Developer I: Introduction to Containers with Podman (DO188) 
    - OCP Administration advanced: Red Hat OpenShift Administration II: Operating a Production Kubernetes Cluster (DO280)
- [Kubernetes Documentation](https://kubernetes.io/docs)


---

🎉 **Congratulations!** 🎉 You've completed the OpenShift 101 lab. Keep experimenting, keep learning, and remember: understanding *why* is more valuable than memorizing *how*.
