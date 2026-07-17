# When Things Don’t Go as Planned: OpenShift Troubleshooting


Real-world operations involve diagnosing and fixing issues quickly. This hands-on troubleshooting section builds confidence in using Bob and OpenShift tools to resolve common problems.

From personal experience, to get a good first idea about a problem, I'd always recommend checking the below commands as

💡 **Golden Troubleshooting Rule**  
```bash
oc get pods → What is failing?
oc describe pod <pod> → Why is it failing? 
oc logs → What is the application doing? 
oc get events → What just happened in the cluster?  
```

---
Next, let's learn how to diagnose an OpenShift issue with Bob:

### Prompt

```
Let's practice troubleshooting:
1. Show me all the ways to observe the hello application:
   - Pod logs
   - Events
   - Resource usage (CPU/memory)
   - Service endpoints
   - Route status

2. Simulate a failure by updating the deployment with an invalid image

3. Walk me through diagnosing the issue:
   - What's the pod status?
   - What do the events say?
   - How would you fix it?

4. Explain the troubleshooting hierarchy: Deployment → ReplicaSet → Pod → Container
```

### What to Observe

Bob should:
1. Show observability commands:
   - `oc logs <pod>`
   - `oc get events`
   - `oc top pods` (if metrics-server available)
   - `oc get endpoints`
   - `oc describe route`
2. Break the deployment: Simulate failure by updating the deployment with an invalid image
3. Diagnose:
   - `oc get pods` - Shows ImagePullBackOff
   - `oc describe pod` - Shows image pull failure
   - `oc get events` - Shows error details
4. Fix: `oc rollout undo deployment/hello`

Watch for:
- Pod stuck in ImagePullBackOff or ErrImagePull
- Events showing "Failed to pull image"
- Rollback restoring previous working state

### Checkpoint

- ✅ Multiple observability methods demonstrated
- ✅ Failure simulated and diagnosed
- ✅ Root cause identified from events
- ✅ Rollback successful

### Reflection

1. **What's the troubleshooting hierarchy?** Where do you start when something breaks?
   - *Hint: Start at the top (Deployment) and work down to the container*

2. **Why are events so important?** What information do they provide?
   - *Hint: Events show the control plane's actions and decisions*

3. **What's the difference between `oc logs` and `oc get events`?**
   - *Hint: Logs show application output; events show Kubernetes actions*


---
🧠 **Key Insight**

Most OpenShift issues are not random.

They are the result of the system enforcing:
- desired state
- resource constraints
- configuration rules

If you understand how the system reconciles state, you can predict and fix most failures.


---
## Troubleshooting Quick Reference

| Symptom | Likely Cause | Diagnostic Command | Fix |
|---------|--------------|-------------------|-----|
| Pod stuck in Pending | Insufficient resources or scheduling constraints | `oc describe pod` | Check resource requests, node capacity, affinity rules |
| Pod in ImagePullBackOff | Cannot pull image | `oc describe pod`, `oc get events` | Verify image name, registry access, pull secrets |
| Pod in CrashLoopBackOff | Application crashes on startup | `oc logs <pod>`, `oc describe pod` | Check application logs, liveness probe, resource limits |
| Pod stuck in OOMKilled | Memory limit too low or memory spike | `oc describe pod`, `oc adm top pod` | Increase limits/requests or optimize memory usage |
| Service not accessible | Endpoints missing or selector mismatch | `oc get endpoints`, `oc describe svc` | Verify pod labels match service selector |
| Route returns 503 | No healthy pods or selector mismatch | `oc get pods`, `oc describe route` | Check pod readiness, service endpoints, labels |
| HPA shows "unknown" | No metrics or missing resource requests | `oc describe hpa`, `oc top pods` | Set resource requests, verify metrics-server |
| SCC violation | Security context incompatible with SCC | `oc describe pod`, `oc get events` | Configure proper securityContext |
| Permission denied | RBAC insufficient | `oc auth can-i <verb> <resource>` | Create appropriate role and rolebinding |

---


## Using Bob Effectively
- **Be very specific about what you want** in your prompts
- **Always bring the right context that is needed**
- **Verify changes** before applying them and don't forget to test along the way
- Consider adding **[custom rules](https://internal.bob.ibm.com/docs/ide/features/custom-rules)** to e.g. operate with a **least-privilege mindset**, even when admin credentials are available or **never assume** an action is safe because it is technically permitted by the current role or to change the conversation style as in [this example](./resources/Context.md).


⚠️ Bob can assist with troubleshooting, but understanding the system is essential to ask the right questions and interpret results correctly ⚠️
