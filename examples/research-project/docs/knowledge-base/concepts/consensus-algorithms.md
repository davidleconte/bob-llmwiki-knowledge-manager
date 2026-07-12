# Consensus Algorithms

## Overview
Consensus algorithms enable distributed systems to agree on a single value or state, even in the presence of failures.

## Key Points
- Fundamental to distributed systems
- Ensure consistency across replicas
- Handle network partitions and failures
- Trade-offs between performance and fault tolerance
- Critical for blockchain and databases

## Details

### Problem Statement
In a distributed system with multiple nodes:
- Nodes may fail or become unreachable
- Network messages may be delayed or lost
- Nodes must agree on a single value
- Agreement must be reached despite failures

### Key Properties
1. **Agreement**: All correct nodes decide on the same value
2. **Validity**: Decided value must be proposed by some node
3. **Termination**: All correct nodes eventually decide
4. **Integrity**: Each node decides at most once

### Major Algorithms

#### Paxos
- Developed by Leslie Lamport (1989)
- Proven correct but complex
- Used in Google Chubby, Apache ZooKeeper
- Handles crash failures

#### Raft
- Developed by Ongaro and Ousterhout (2014)
- Designed for understandability
- Leader-based approach
- Used in etcd, Consul
- Handles crash failures

#### PBFT (Practical Byzantine Fault Tolerance)
- Handles Byzantine failures
- More complex than crash-only algorithms
- Used in blockchain systems
- Higher message complexity

## Related Documents
- [Byzantine Fault Tolerance](./byzantine-fault-tolerance.md)
- [Paxos Analysis](../research/paxos-analysis-2026-06.md)
- [Raft Comparison](../research/raft-comparison-2026-07.md)

## References
- Lamport, L. (1998). "The Part-Time Parliament"
- Ongaro, D., & Ousterhout, J. (2014). "In Search of an Understandable Consensus Algorithm"
