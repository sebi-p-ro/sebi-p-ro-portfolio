<div align="center">

# Victor Kipruto Rop — Data Engineering Portfolio

**A portfolio of data engineering experiments and reusable analytics assets spanning banking, telecom, and public-sector domains. The repository includes ETL scripts, dbt models, dashboards, and infrastructure examples rather than one single production deployment.**

[![CI/CD](https://github.com/Victor-Kipruto-Rop/victor-kipruto-rop-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/Victor-Kipruto-Rop/victor-kipruto-rop-portfolio/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![dbt](https://img.shields.io/badge/dbt-1.7-FF694B?style=flat-square&logo=dbt&logoColor=white)](https://getdbt.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Victor-Kipruto-Rop/victor-kipruto-rop-portfolio?style=flat-square)](https://github.com/Victor-Kipruto-Rop/victor-kipruto-rop-portfolio/commits/main)
[![Stars](https://img.shields.io/github/stars/Victor-Kipruto-Rop/victor-kipruto-rop-portfolio?style=flat-square)](https://github.com/Victor-Kipruto-Rop/victor-kipruto-rop-portfolio/stargazers)

</div>

---

## Table of Contents

- [Live Dashboards](#-live-dashboards)
- [Architecture](#️-architecture)
- [Projects](#-projects)
- [Engineering Standards](#-engineering-standards)
- [Infrastructure & IaC](#-infrastructure--iac)
- [Data Sources](#️-data-sources)
- [Tech Stack](#️-tech-stack)
- [Roadmap](#-roadmap)
- [Contact](#-contact)

---

## 📊 Live Dashboards

| Dashboard | Link | Description |
|---|---|---|
| **Executive Financial Summary** | [🚀 View](https://kipruto45-victor-kipruto-rop-portfolio-g8pspygfpttsbfggjaadwy.streamlit.app/) | Unified 2025 audited KPIs across KCB, Absa Kenya, and Equity Group |
| **Absa Bank Kenya** | [🔴 View](https://kipruto45-victor-kipruto-rop-portfolio-cc6ye8wlqrt2vtpsdndigd.streamlit.app/) | Financial KPIs, Risk/Capital ratios, and Open Banking API adoption metrics |
| **Equity Group Pan-Africa** | [🌍 View](https://kipruto45-victor-kipruto-rop-portfolio-g8pspygfpttsbfggjaadwy.streamlit.app/) | Regional profitability, mobile adoption, and Kenya transaction matrix |
| **KCB Group Integrated** | [🦁 View](https://kipruto45-victor-kipruto-rop-portfolio-g8pspygfpttsbfggjaadwy.streamlit.app/) | Consolidated performance tracking and M-Pesa loan book analytics |
| **KRA Revenue & Trade** | [🇰🇪 View](https://kipruto45-victor-kipruto-rop-portfolio-g8pspygfpttsbfggjaadwy.streamlit.app/) | Tax revenue monitoring, customs trade flows, and economic indicators |

---

## 🏗️ Architecture

```mermaid
graph LR
    subgraph Sources["Data Sources"]
        A[CBK / NSE / KNBS Reports]
        B[M-Pesa / Safaricom APIs]
        C[KRA Revenue Data]
        D[Real-Time Kafka Streams]
    end

    subgraph Ingestion["Ingestion Layer"]
        E[Python ETL Scripts]
        F[Kafka Consumers]
        G[PDF / API Parsers]
    end

    subgraph Orchestration["Orchestration"]
        H[Apache Airflow DAGs]
    end

    subgraph Storage["Bronze Layer — Raw"]
        I[(PostgreSQL 15)]
    end

    subgraph Transform["Silver → Gold — dbt"]
        J[Staging Models]
        K[Intermediate Models]
        L[Mart Models]
    end

    subgraph Output["Output Layer"]
        M[Streamlit Dashboards]
        N[Isolation Forest — Fraud ML]
        O[Float Liquidity Forecasting]
    end

    subgraph Infra["Infrastructure"]
        P[Terraform — IaC]
        Q[Kubernetes — k8s/]
        R[GitHub Actions — CI/CD]
    end

    Sources --> Ingestion
    Ingestion --> H
    H --> Storage
    Storage --> J --> K --> L
    L --> M
    L --> N
    L --> O
    P --> Storage
    P --> Q
    R --> H
    R --> J
```

Full architecture detail in [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## 📂 Projects

| Project | Domain | Key Metric | Stack | Dashboard | Status |
|---|---|---|---|---|---|
| [mpesa_safaricom](./mpesa_safaricom) | Streaming and analytics examples | Batch and streaming-oriented assets | Python, dbt, Airflow | — | 🛠️ Active |
| [absa_bank_kenya](./absa_bank_kenya) | Banking ETL and reporting assets | Example pipelines and dashboards | Python, dbt, PostgreSQL | — | 🧪 Example-oriented |
| [equity_group_etl](./equity_group_etl) | Regional consolidation examples | Multi-country rollup assets | Airflow, PostgreSQL, dbt | — | 🧪 Example-oriented |
| [kcb_group_etl](./kcb_group_etl) | Financials and loan analytics | Core KCB analytics package | Python, SQL, dbt | — | 🛠️ Active |
| [kra_data_engineering](./kra_data_engineering) | Fiscal and trade intelligence | Tax and customs examples | Python, SQL, dbt | — | 🧪 Example-oriented |
| [safaricom_pipeline](./safaricom_pipeline) | Telecom analytics examples | Subscriber and service metrics assets | Python, Spark, SQL | — | 🧪 Example-oriented |
| [kenya_banking_sector](./kenya_banking_sector) | Macro-financial analytics workspace | Sector-wide templates and notebooks | Python, BI, Analytics | — | 🧪 Partially scaffolded |
| [fraud_anomaly_detection](./mpesa_safaricom/fraud_anomaly_detection) | Fraud detection examples | Rule-based and ML-oriented assets | Python, Scikit-learn, PostgreSQL | — | 🧪 Example-oriented |
| [float_liquidity_forecasting](./mpesa_safaricom/float_liquidity_forecasting) | Forecasting experiments | Time-series forecasting examples | Python, Prophet, dbt | — | 🧪 Example-oriented |
| [agent_network_analytics](./mpesa_safaricom/agent_network_analytics) | Agent liquidity analytics | Network and coverage examples | Python, SQL, dbt | — | 🧪 Example-oriented |
| [remittance_analytics](./mpesa_safaricom/remittance_analytics) | Cross-border analytics | Corridor and remittance examples | Python, SQL, dbt | — | 🧪 Example-oriented |
| [merchant_intelligence_platform](./mpesa_safaricom/merchant_intelligence_platform) | Merchant segmentation examples | RFM and segmentation assets | Python, SQL, dbt | — | 🧪 Example-oriented |
| [mpesa_enterprise_projects/pan-african-lakehouse](./mpesa_enterprise_projects/pan-african-lakehouse) | Minimal medallion lakehouse example | Bronze/silver/gold starter project | dbt, PostgreSQL, Terraform | — | 🟡 Minimal example |

---

## ⚙️ Engineering Standards

| Standard | Implementation | Coverage |
|---|---|---|
| **CI/CD** | GitHub Actions workflows for linting and dbt parsing checks | Selected projects |
| **Data Quality** | dbt schema tests and SQL conventions are present in several projects | Partial |
| **Unit Testing** | Pytest coverage for ingestion and transformation helpers exists in places | Partial |
| **Code Style** | SQLFluff and Python formatting conventions are documented for the main projects | Partial |
| **Fraud Detection** | Rule-based and model-oriented fraud examples are included | Example level |
| **Secrets Management** | `.env` examples are included and local credentials remain outside source control | In practice |
| **Containerisation** | Docker Compose files are present for a subset of projects | Partial |
| **Orchestration** | Airflow-style DAGs appear in several subprojects | Partial |

---

## 🏗️ Infrastructure & IaC

Terraform (HCL) provisions the core infrastructure across all projects:

- **PostgreSQL 15** — managed database for raw ingestion and dbt transformation output
- **Streamlit deployments** — dashboard hosting with environment variable injection
- **Kubernetes manifests** (`k8s/`) — deployment and scaling configs for PostgreSQL and Streamlit pods
- **GitHub Actions runners** — CI/CD pipeline automation for linting, testing, and deployment

See `k8s/` for Kubernetes manifests and Terraform configs within each project directory.

---

## 🛰️ Data Sources

| Source | Data Type | Update Frequency |
|---|---|---|
| **Central Bank of Kenya (CBK)** | Bank Supervision Reports, Mobile Credit Statistics, Prudential Guidelines | Annual / Quarterly |
| **Kenya Revenue Authority (KRA)** | Monthly Revenue Reports, Customs Rules of Origin | Monthly |
| **Kenya National Bureau of Statistics (KNBS)** | Leading Economic Indicators — Inflation, Trade Volume, GDP | Monthly |
| **International Trade Centre (ITC)** | TradeMap trade benchmarks and company directories | Quarterly |
| **Safaricom / M-Pesa** | Open API specs, Sustainability Reports, GSMA mobile money datasets | Annual / Real-time |
| **Nairobi Securities Exchange (NSE)** | Audited financial filings for listed commercial banks | Annual |

---

## 🛠️ Tech Stack

<table>
  <tr>
    <td valign="top" width="50%">
      <strong>Ingestion & Processing</strong><br/>
      <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
      <img src="https://img.shields.io/badge/Apache_Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white"/>
      <img src="https://img.shields.io/badge/Apache_Spark-E25A1C?style=flat-square&logo=apachespark&logoColor=white"/>
      <img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white"/>
    </td>
    <td valign="top" width="50%">
      <strong>Orchestration & Transformation</strong><br/>
      <img src="https://img.shields.io/badge/Apache_Airflow-017CE1?style=flat-square&logo=apache-airflow&logoColor=white"/>
      <img src="https://img.shields.io/badge/dbt-FF694B?style=flat-square&logo=dbt&logoColor=white"/>
      <img src="https://img.shields.io/badge/SQL-CC292B?style=flat-square&logo=sqlite&logoColor=white"/>
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <strong>Storage & Lakehouse</strong><br/>
      <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white"/>
      <img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white"/>
      <img src="https://img.shields.io/badge/Delta_Lake-003366?style=flat-square&logoColor=white"/>
    </td>
    <td valign="top" width="50%">
      <strong>Infrastructure & DevOps</strong><br/>
      <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"/>
      <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white"/>
      <img src="https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white"/>
      <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white"/>
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <strong>Analytics & Visualisation</strong><br/>
      <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white"/>
      <img src="https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white"/>
    </td>
    <td valign="top" width="50%">
      <strong>ML & Data Quality</strong><br/>
      <img src="https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white"/>
      <img src="https://img.shields.io/badge/Great_Expectations-FF6B35?style=flat-square&logoColor=white"/>
      <img src="https://img.shields.io/badge/dbt_Tests-FF694B?style=flat-square&logo=dbt&logoColor=white"/>
    </td>
  </tr>
</table>

---

## 🗺️ Roadmap

| Timeline | Item | Status |
|---|---|---|
| Q3 2026 | Apache Flink migration for sub-100ms streaming latency | 🟡 Planned |
| Q3 2026 | OpenLineage integration for end-to-end data lineage tracking | 🟡 Planned |
| Q3 2026 | Per-project individual Streamlit URLs — fix shared dashboard links | 🟡 Planned |
| Q4 2026 | Great Expectations integration across all ingestion layers | 🟡 Planned |
| Q4 2026 | Real-time fraud scoring via Kafka Streams (replace batch Isolation Forest) | 🟡 Planned |
| Q1 2027 | Apache Iceberg migration for time-travel queries on the lakehouse | 🟡 Planned |
| Q1 2027 | dbt Semantic Layer + MetricFlow for unified business metrics | 🟡 Planned |

---

## 📬 Contact

**Victor Kipruto Rop** — Data Engineer, Nairobi, Kenya 🇰🇪

[![GitHub](https://img.shields.io/badge/GitHub-Victor--Kipruto--Rop-181717?style=flat-square&logo=github)](https://github.com/Victor-Kipruto-Rop)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-victor--rop-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/victor-rop-4920b4399)
[![Portfolio](https://img.shields.io/badge/Portfolio-victor--kipruto--rop.github.io-0e75b6?style=flat-square)](https://victor-kipruto-rop.github.io/victor-resum-web/)
[![Email](https://img.shields.io/badge/Email-kiprutovictor39@gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:kiprutovictor39@gmail.com)

📞 +254 723 484 552

---

## 📜 License

MIT License — see [LICENSE](./LICENSE) for details.

---

<div align="center">
  <sub>Built in Nairobi, Kenya 🇰🇪 · <a href="https://victor-kipruto-rop.github.io/victor-resum-web/">Portfolio</a> · <a href="https://www.linkedin.com/in/victor-rop-4920b4399">LinkedIn</a></sub>
</div>
