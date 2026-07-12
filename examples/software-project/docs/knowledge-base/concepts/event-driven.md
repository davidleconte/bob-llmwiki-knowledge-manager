# Event-Driven Architecture

## Overview
Event-driven architecture is a software design pattern where services communicate through events, enabling loose coupling and asynchronous processing.

## Key Points
- Services emit events when state changes occur
- Other services subscribe to relevant events
- Asynchronous, non-blocking communication
- Enables eventual consistency
- Supports scalability and resilience

## Details

### Our Implementation
We use RabbitMQ as our message broker for event-driven communication:

**Event Types:**
- `order.created` - New order placed
- `payment.processed` - Payment completed
- `inventory.updated` - Stock levels changed
- `user.registered` - New user account

**Event Flow Example:**
1. User places order → Order Service emits `order.created`
2. Payment Service subscribes → processes payment
3. Payment Service emits `payment.processed`
4. Inventory Service subscribes → updates stock
5. Notification Service subscribes → sends confirmation email

### Benefits
- Loose coupling between services
- Scalability through async processing
- Resilience through message persistence
- Easy to add new subscribers

### Challenges
- Eventual consistency complexity
- Event ordering guarantees
- Debugging distributed flows
- Message schema evolution

## Related Documents
- [Microservices Architecture](./microservices.md)
- [CQRS Pattern](./cqrs-pattern.md)

## References
- [Event-Driven Architecture Patterns](https://martinfowler.com/articles/201701-event-driven.html)
