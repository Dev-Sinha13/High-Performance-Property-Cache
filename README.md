# ⚡ High Performance Property Cache

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![gRPC](https://img.shields.io/badge/RPC-gRPC-244c5a.svg?logo=google&logoColor=white)](https://grpc.io/)
[![Flask](https://img.shields.io/badge/Framework-Flask-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker Compose](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED.svg?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

> A highly-available, distributed caching gateway sitting in front of a gRPC microservice ecosystem. It load-balances external API requests, caches geographic property data in memory, and seamlessly handles node failures for uninterrupted uptime.

## 📖 Overview

In data-heavy ecosystems, querying raw databases directly for frequently accessed records causes massive bottlenecks. This project solves that by standing up an intelligent caching layer in front of two replicated remote procedure call (RPC) dataset nodes. 

Built around a simulated microservices architecture using **Docker Compose**, the application natively handles network partitioning, fault tolerance, and Last-Recently-Used (LRU) memory optimization.

## ✨ Key Features

- **Blazing Fast In-Memory Caching:** Radically reduces latency for repeated Zip Code queries by serving payloads directly from local memory variables if they appear in recent request logs.
- **Round-Robin Load Balancing:** Automatically routes subsequent inbound HTTP requests evenly between `dataset-1` and `dataset-2` to maximize hardware utilization.
- **Automatic Failover & Re-tries:** If a backend RPC node experiences downtime or network segmentation, the Flask gateway automatically catches the `grpc.RpcError`, instantly toggles to the surviving replica, and retries the connection until fulfilled.
- **Protocol Buffer Serialization:** Communication between the API gateway and backend records utilizes `.proto` definitions, ensuring data payloads are incredibly small and fast compared to standard JSON REST APIs.

## 🏗️ Architecture & Tech Stack

- **gRPC (`PropertyLookup.proto`)**: Defines the strict typing boundary for the distributed datasets. 
- **Flask (`cache.py`)**: The public-facing HTTP API server that holds the global caching state map.
- **Docker Compose (`docker-compose.yml`)**: Orchestrates the local cluster, assigning the DNS names `dataset-1` and `dataset-2` so the cache layer can discover them across the virtual Docker network.

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose**

### Deployment

1. **Spin up the Cluster**
   This command automatically builds the dataset nodes, the cache node, and connects them securely on an internal network.
   ```bash
   docker-compose up -d --build
   ```

2. **Query the Gateway**
   Target the listening Flask application on your `localhost`.
   
   *Querying Zip Code 53703 for 5 properties:*
   ```bash
   curl "http://localhost:8080/lookup/53703?limit=5"
   ```

3. **Observe the Results**
   The returned JSON will explicitly mention its source: `1` (node 1), `2` (node 2), or `cache` (in-memory hit).

## 📂 Project Structure

```text
.
├── PropertyLookup.proto      # Protocol buffer definitions
├── cache.py                  # Highly available Flask API gateway
├── dataset.py                # gRPC server simulating backend datasets
├── Dockerfile.cache          # Build instructions for the API gateway
├── Dockerfile.dataset        # Build instructions for the data nodes
├── docker-compose.yml        # Multi-node orchestration configuration
└── README.md
```
