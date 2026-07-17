# Multi-stage build for Agentic Stock Trader
FROM maven:3.8.6-openjdk-11-slim AS build

WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code and build
COPY src ./src
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:11-jre-jammy

WORKDIR /app

# Copy the built jar from build stage
COPY --from=build /app/target/agentic-stock-trader-1.0-SNAPSHOT.jar /app/agentic-stock-trader.jar

# Expose port 8080 for web UI
EXPOSE 8080

# Run the Spring Boot application
ENTRYPOINT ["java", "-jar", "/app/agentic-stock-trader.jar"]

# Made with Bob
