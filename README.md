# Eco-Parking Automated EV Infrastructure Ecosystem

![Architecture Status](https://img.shields.io/badge/Architecture-Distributed%20Edge%20%2F%20Microservices-blue?style=for-the-badge&logo=architecture)
![Backend Stack](https://img.shields.io/badge/Backend-Django%20%2F%20Python%203.9-green?style=for-the-badge&logo=django)
![Edge Computing](https://img.shields.io/badge/Edge-Raspberry%20Pi%204%20%2F%20Linux%20Embedded-orange?style=for-the-badge&logo=raspberrypi)
![Network Security](https://img.shields.io/badge/Network%20Security-OpenVPN%20%2F%20Air--Gapped%20CA-red?style=for-the-badge&logo=openvpn)
![Observability](https://img.shields.io/badge/Observability-Telegraf%20%2F%20InfluxDB%20%2F%20Grafana-purple?style=for-the-badge&logo=grafana)

A production-grade, highly resilient Hardware-Software Complex (HSC) engineered for the automated management, orchestration, and billing of a geographically distributed network of commercial electric vehicle (EV) charging stations. The system provides a seamless end-to-end telemetry and control pipeline, linking low-level hardware processing at the edge with high-throughput cloud infrastructure and secure financial processing.

---

## 🗺️ System Topology & Monorepo Architecture

The ecosystem enforces a strict separation of concerns, split across an autonomous **Edge Compute Grid**, an enterprise **Cloud Core**, and a real-time **Observability Framework**. To bypass Carrier-Grade NAT (CGNAT) on cellular GSM links in the field, all edge units communicate over an encrypted private virtual overlay network network topology.

### 📂 Repository Directory Directory Matrix
This monorepo consolidates all microservices and drivers required to run the infrastructure:

*   **`/-ttlock-investigation`** — R&D core focused on the reverse-engineering, security analysis, and integration protocols of Bluetooth Low Energy (BLE) smart lock systems, evaluating key exchange security for parking hardware.
*   **`/bot-assistant`** — Asynchronous automation and notification daemon (Telegram/Slack integration) providing real-time infrastructure telemetry, error warnings, and remote hardware override capabilities for support engineers.
*   **`/deployment`** — Production orchestration manifests containing multi-container `docker-compose` topologies, Caddy reverse-proxy configurations with automated ACME SSL generation, and monitoring infrastructure definitions.
*   **`/landing`** — Ultra-responsive, high-conversion public corporate interface (`eco-nrg.store`) optimized for client acquisition and localized edge branding.
*   **`/manual-control`** — Hardened administrative utility kit enabling low-level manual intervention over physical station states, bypassing standard automated scheduler logic for diagnostics.
*   **`/parklock-control`** — Hardware-interfacing driver module managing target BLE scans, characteristic writes, and status checks for automated ground parking locks.
*   **`/server`** — High-availability cloud core backend developed in Python/Django, driving the central RESTful API engine (`api.eco-nrg.store`), processing fintech webhooks, and exposing a secure, granular administrative control panel (`/my_admin/`).
*   **`/station`** — Low-level asynchronous daemon mesh running natively on embedded Raspberry Pi 4 nodes, responsible for localized hardware polling and IPC.
*   **`/station_ui`** — Embedded, hardware-accelerated touchscreen GUI built with PyQt5 and declarative QML, synchronizing state locally via a high-speed in-memory Redis data bus.
*   **`/web_app`** — Progressive Web App (PWA) (`charge.eco-nrg.store`) empowering EV drivers to geolocate active stations, authenticate via SMS, fund accounts, initiate charging loops, and monitor live security camera feeds.
*   **`/wiki`** — Exhaustive architectural documentation base, engineering runbooks, database schemas, and interface control documents (ICDs).

---

## 🏗️ Technical Architecture Flow

```mermaid
graph TD
    %% Cloud Core Service Infrastructure
    subgraph Cloud_Core [Selectel & RuVDS Distributed Cloud Layer]
        Caddy[Caddy Edge Proxy / Automated SSL] <--> |Internal Routing| Django[Django REST API Core Engine]
        Django <--> |State Persistence| DB[(Central Database Cluster)]
        OpenVPN_Srv[Secure OpenVPN Gateway Server] <--> Django
    end

    %% Air-Gapped Security Pipeline
    subgraph PKI_Security [Isolated PKI Environment]
        CA_Serv[Air-Gapped Certificate Authority / ca-serv]
    end
    CA_Serv --> |Manual CSR Cryptographic Signing| OpenVPN_Srv

    %% Edge IoT Layer
    subgraph Edge_Station [Raspberry Pi 4 Embedded Node Grid]
        R_Pi[Raspberry Pi 4 / Linux Architecture] <--> |Encrypted GSM Tunnel| OpenVPN_Srv
        
        %% Local Hardware Protocols
        R_Pi --> |RS-485 / Modbus RTU Protocol| Meter[Mercury 234 Industrial Smart Meter]
        R_Pi --> |Bluetooth Low Energy / BLE| Parklock[Automated Ground Parking Lock]
        R_Pi --> |Low-level GPIO / PWM Signaling| LEDs[Dynamic RGB Status LED Array]
        R_Pi --> |Digital Signal Parsing| Sensors[Ultrasonic & Lidar Proximity Arrays]
        R_Pi --> |RTSP Video Streaming| IP_Cam[On-Site IP Cameras & Local DVR]
        R_Pi --> |Control Pilot / Proximity Detection| Connector[EV Charging Interface / IEC 62196]
        R_Pi --> |Local Graphics Pipeline| UI[PyQt5 & QML Touch User Interface]
        R_Pi --> |IPC / High-Speed Message Bus| Redis[(Local In-Memory Redis Cache)]
    end

    %% Enterprise Observability Pipeline
    subgraph Observability_Stack [Observability & Analytics Architecture]
        R_Pi --> |System & Domain Telemetry| Telegraf[Telegraf Agent Daemon]
        Telegraf --> |High-Frequency Ingestion Data| InfluxDB[(InfluxDB Time-Series Cluster)]
        InfluxDB --> |Advanced Analytical Dashboards| Grafana[Grafana Visualization Server]
    end

    %% Fintech Integration Layer
    subgraph Fintech_Gateway [Banking & Notification APIs]
        Django <--> |REST API / Secure Webhooks / FZ-54| Alfa[Alfa-Bank Acquiring Gateway]
        Django <--> |Automated Invoicing / Ledgers / Refunds| PayKeeper[PayKeeper Billing System]
        Django --> |Transactional OTP Verification| SMS[Sms.ru Gateway]
    end
