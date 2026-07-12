# Byzantine Fault Tolerance

## Overview
Byzantine Fault Tolerance (BFT) is the ability of a distributed system to reach consensus even when some nodes behave arbitrarily or maliciously.

## Key Points
- Handles arbitrary failures (not just crashes)
- Nodes may send conflicting information
- Requires 3f+1 nodes to tolerate f failures
- Higher complexity than crash-only algorithms
- Essential for blockchain and untrusted environments

## Details

### Byzantine Generals Problem
Classic problem formulated by Lamport et al. (1982):
- Multiple generals must coordinate attack
- Some generals may be traitors
- Must reach consensus despite traitors
- Impossible with 1/3 or more traitors

### PBFT Algorithm
Practical Byzantine Fault Tolerance (Castro & Liskov, 1999):
- Three-phase protocol: pre-prepare, prepare, commit
- Requires 3f+1 replicas for f failures
- O(n²) message complexity
- Used in Hyperledger Fabric

### Modern BFT Variants
- **HotStuff**: Linear message complexity
- **Tendermint**: Used in Cosmos blockchain
- **Istanbul BFT**: Used in Ethereum
- **Algorand**: Probabilistic BFT

## Related Documents
- [Consensus Algorithms](./consensus-algorithms.md)

## References
- Castro, M., & Liskov, B. (1999). "Practical Byzantine Fault Tolerance"
- Lamport, L., et al. (1982). "The Byzantine Generals Problem"
