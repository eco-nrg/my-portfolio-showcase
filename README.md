# Eco-Parking Infrastructure Ecosystem

![Architecture Status](https://img.shields.io/badge/Architecture-Distributed%20IoT%20%2F%20Microservices-blue)
![Backend Stack](https://img.shields.io/badge/Backend-Django%20%2F%20Python-green)
![Edge Computing](https://img.shields.io/badge/Edge-Raspberry%20Pi%204%20%2F%20Linux%20Embedded-orange)
![Network Security](https://img.shields.io/badge/Network%20Security-OpenVPN%20%2F%20Custom%20CA-red)

A production-grade, highly scalable Hardware-Software Complex (HSC) engineered for the automation, orchestration, and monetization of a distributed network of commercial electric vehicle (EV) charging stations. The system delivers a complete end-to-end telemetry and control pipeline: from low-level hardware interfacing via BLE/Modbus protocols on the edge to cloud-based payment processing and real-time network observability[cite: 15, 17, 18, 19].

---

## 🏗 System Architecture & Repository Structure

The ecosystem is architected around a strict separation of concerns split across **Edge Compute Nodes**, **Cloud Core Services**, and an **Observability Pipeline**[cite: 15, 18, 19]. Since edge charging stations operate in the field via cellular GSM modems behind carrier-grade NAT, they are securely aggregated into a private, encrypted virtual overlay network.

The repository is organized into the following specialized modules (as mapped above):
*   `/landing` — Corporate public website and promotional engine for `eco-nrg.store`.
*   `/web_app` — Client-facing mobile web application (`charge.eco-nrg.store`) for station activation, account funding, and live CCTV stream viewing[cite: 19, 20].
*   `/server` & `/deployment` — Central cloud core orchestration, containerized Django API (`api.eco-nrg.store`), database schemas, and global deployment configs[cite: 18, 19, 20].
*   `/station` — Low-level asynchronous Python backend engine running locally on field hardware.
*   `/station_ui` — Hardware-accelerated PyQt5/QML graphical user interface framework rendering on the physical station display.
*   `/parklock-control` & `/manual-control` — Dedicated modules driving wireless hardware interaction and diagnostic control loops.

```mermaid
graph TD
    %% Cloud Infrastructure Layer
    subgraph Cloud_Core [Selectel & RuVDS Cloud Infrastructure]
        Caddy[Caddy Reverse Proxy / HTTPS] <--> |Port Routing| Django[Django API Engine / Cloud Core]
        Django <--> |Admin Panel /my_admin/| DB[(Central Database)]
        OpenVPN_Srv[OpenVPN Gateway Server / 193.42.113.39] <--> Django
    end

    %% Security & Management Layer
    subgraph Security_Conveyor [Isolated Security CA]
        CA_Serv[Isolated Certificate Authority VM / ca-serv]
    end
    CA_Serv --> |Cryptographic Sign / Easy-RSA| OpenVPN_Srv

    %% Edge IoT Layer
    subgraph Edge_Station [Distributed IoT Stations / Regional Edge Grid]
        R_Pi[Raspberry Pi 4 / Embedded Linux / Overlay Subnet] <--> |GSM Modem / Encrypted Tunnel| OpenVPN_Srv
        
        %% Local Hardware Connections
        R_Pi --> |RS-485 / Modbus Protocol| Meter[Mercury 234 Smart Meter]
        R_Pi --> |Bluetooth Low Energy - BLE| Parklock[Automated Ground Barrier / Parklock]
        R_Pi --> |Low-level GPIO / PWM via pigpio| LEDs[Dynamic RGB Status Display]
        R_Pi --> |Analog / Digital Signals| Sensors[Ultrasonic & Lidar Distance Sensors]
        R_Pi --> |CCTV Stream / RTSP| IP_Cam[IP Cameras & Local DVR]
        R_Pi --> |Pilot Signal / Charging Control| Connector[Tesla Wall Connector / IEC 62196]
        R_Pi --> |Local GUI Runtime| UI[PyQt5 / QML Embedded Display Interface]
        R_Pi --> |In-Memory Bus| Redis[(Local Redis Cache)]
    end

    %% Observability Pipeline
    subgraph Metrics_Pipeline [Observability & Analytics Stack]
        R_Pi --> |Metrics Export| Telegraf[Telegraf Daemon Agent]
        Telegraf --> |Time-Series Data Stream| InfluxDB[(InfluxDB Cluster)]
        InfluxDB --> |Data Visualization| Grafana[Grafana Dashboard Engine]
    end

    %% Fintech Integration Layer
    subgraph Fintech_Gateway [Acquiring & Billing Gateways]
        Django <--> |REST API / Callbacks / Compliance| Alfa[Banking Acquiring API]
        Django <--> |Invoicing / E-mail Ledger / Refunds| PayKeeper[PayKeeper Processing System]
        Django --> |Transactional SMS Verification| SMS[Sms.ru Gateway]
    end
