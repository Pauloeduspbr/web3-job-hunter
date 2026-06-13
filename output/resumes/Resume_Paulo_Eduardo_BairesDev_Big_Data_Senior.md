# Paulo Eduardo dos Santos

**Senior Big Data Engineer | Spark & Hadoop | Cloud Data Platforms**

*ATS Match: 85% — Big Data Senior (Remote) @ BairesDev*

São Paulo, Brazil — 100% Remote | +55 11 91526-7337 | paulo_eduardosp@yahoo.com.br
LinkedIn: linkedin.com/in/paulo--eduardo | GitHub: github.com/Pauloeduspbr

---

## PROFESSIONAL SUMMARY

Senior Big Data Engineer with 9 years as a developer and 8+ years in Big Data, writing highly efficient Apache Spark/PySpark jobs that process terabytes of data and optimizing workloads on large Hadoop clusters (Cloudera/Hortonworks) for banks and telecoms handling millions of daily transactions. Hands-on with both batch and streaming (real-time) processing, large-scale data loads with embedded data quality, and resilient environments at 99.9% uptime SLA (Banco do Brasil) alongside production AWS platforms. Clean, efficient Python; experienced mentor and technical lead in distributed, multicultural teams.

---

## TECHNICAL SKILLS

**Big Data:** Apache Spark (TB-scale job optimization), PySpark, SparkSQL, Hadoop (Cloudera/Hortonworks), Hive, HDFS, Impala, Kafka, Sqoop, Flume

**Languages:** Python (advanced), SQL (advanced), Shell Script, Scala

**AWS & DevOps:** EMR / EMR Serverless, S3, Glue, Athena, Redshift, Lambda, Kinesis, CloudWatch; Docker, Kubernetes, Terraform, Ansible, CI/CD — resiliency, security, high availability

**Streaming & Data Quality:** batch + streaming ingestion (Kafka, Kinesis), CDC, large-scale incremental loads, data quality frameworks, observability (metrics, alerts, log handlers)

**Analytics & ML Support:** pipelines feeding machine learning and analytics workloads; A/B test analysis with quality-assured datasets

**Warehouses & Databases:** Snowflake, BigQuery, Redshift, PostgreSQL, Oracle, Teradata, Cassandra, MongoDB, HBase

**Architecture:** Data Lake & Lakehouse (Bronze/Silver/Gold), Delta Lake, Apache Iceberg, dimensional modeling, cloud migration (on-prem → cloud)

**Orchestration & Transformation:** Apache Airflow, dbt, NiFi, Talend

**Visualization:** Power BI, QlikSense, Tableau, Grafana

---

## PROFESSIONAL EXPERIENCE

### Data Engineer — BRQ
**Jul 2025 – Present | Remote, Brazil**

**RD Saúde — Healthcare Data Lake (Customer 360)**
- Developed PySpark/SparkSQL pipelines for large-scale ingestion, transformation, and consolidation of clinical data on Apache Iceberg/S3 with Medallion architecture (Bronze/Silver/Gold), with Apache Hudi support.
- Orchestrated Airflow DAGs integrated with Spark on Kubernetes, with automated YAML manifest generation through Python builders.
- Built an in-house Data Quality framework (cross-origin validations, light checks) and end-to-end observability (custom log handlers, Spark metrics, exception tracking, AWS SNS + Step Functions) across dev/qa/prod Docker environments.
- Modeled the Customer 360 analytical table integrating CRM, scheduling, events, and interests via Trino, Athena, and Redshift; secured PII/LGPD data with HashiCorp Vault, AWS KMS, and Fernet.

**Itaú — Modernization & Analytics**
- Built ETL pipelines with EMR Serverless and Glue Studio; optimized SQL for performance and supported A/B test analysis with quality-assured datasets for hypothesis validation.

---

### Senior Big Data Specialist / Data Engineer — Stefanini
**Jun 2023 – Jun 2025 | São Paulo, Brazil**

**Banco do Brasil — Big Data Environment Sustainment**
- Sustained and optimized production Cloudera/Hortonworks clusters processing millions of daily financial transactions at **99.9% uptime SLA**.
- Tuned Hive queries via partitioning/bucketing and maintained HDFS; built a reusable Python automation framework that cut operational maintenance time by **40%**; built dbt/Snowflake models with data quality tests.

**AmericaNet — APIs & Data Processing**
- Processed terabyte-scale data with SparkSQL in Databricks; developed a Python Flask REST API and built dbt/Snowflake ELT pipelines, reducing manual intervention by **70%** via Azure Automation.

**Cielo — Dashboard Analytics**
- Developed PySpark scripts for high-volume payment data, Athena external tables over S3 with partitioning, and migrated analytical data to Snowflake with dbt dimensional modeling for Power BI.

**Itaú — ETL Process Refactoring**
- Refactored legacy SQL into Parquet/PySpark jobs, achieving **60% storage reduction**, and built the data catalog with AWS Glue.

**DirectLog — Geolocation System**
- Built Airflow DAGs for batch address processing via the Google Maps API, an authenticated SFTP web interface on EC2, and a caching layer to optimize API calls.

**Brasildev — AWS Data Lake**
- Built a layered Data Lake (Bronze/Silver/Gold) with governance via Lake Formation, a Python ingestion engine integrated with Salesforce, and infrastructure automated with Terraform.

---

### Senior Data Engineer — Natura & Co
**Feb 2022 – Jun 2023 | São Paulo, Brazil**

**E-commerce Pipeline**
- Built EMR Serverless ETL pipelines and complex Airflow DAGs with dynamic dependencies; led the Parquet-to-Delta Lake migration with ACID transactions and schema evolution.
- Modeled dimensional data (customer journey, cohort analysis) across web analytics, transactional, and CRM sources; incremental CDC loads integrated with BI via Redshift.

**Cielo — Cloud Migration & Modernization**
- Mapped Oracle structures to BigQuery, migrated legacy data to Azure Blob Storage, built Azure Data Factory pipelines, and converted complex SQL to distributed PySpark/SparkSQL on Databricks.

**JBS — Data Pipeline Modernization**
- Led a team of engineers; implemented a high-availability NiFi cluster with Active Directory integration, load balancing, and S3↔Redshift data movement for SAP ingestion.

---

### Data Engineer — Enel
**May 2021 – Feb 2022 | Brazil**

**Data Warehouse Migration**
- Migrated the corporate data warehouse from Impala to Redshift with Talend; built QlikSense dashboards, optimized queries, documented ETL, and trained business teams.

---

### Big Data Solutions Architect — Banco do Nordeste
**Jan 2021 – May 2021 | Brazil**

**Corporate Data Lake**
- Designed a Data Lake (raw/stage/analytics) for banking credit systems with an unmanaged Hadoop cluster and Dremio; planned a Cassandra NoSQL structure and integrated legacy systems via DataStage.

**Bradesco — Data Ingestion Framework**
- Updated ingestion-framework scripts for Hive/HBase, developed shell automation, integrated the IBM IWS scheduler, and connected to Teradata for extraction.

---

### Big Data Architect / Engineer — Hospital Sírio-Libanês
**Mar 2019 – Dec 2020 | São Paulo, Brazil**

**Hospital Analytics Platform**
- Built automated Airflow pipelines (Oracle extraction, S3 transfer, format conversion) on AWS (S3, Athena, EMR, Kinesis, Lambda); containerized with Docker, configured Kubernetes for scalability, and implemented SSO integrating AWS Cognito with Azure AD.

**Raízen — Data Ingestion Framework**
- Surveyed the data-pipeline architecture (Azure Data Lake, Databricks, Power BI) and documented SAP integration via SSIS Theobald.

**Dell EMC (Client: Fleury) — Consulting & Training**
- Sustained a Hortonworks environment; hardened security with Kerberos/Ranger, built Oozie monitoring scripts and Grafana dashboards, and trained the client team.

---

### Big Data Technical Lead — Claro Brasil
**Sep 2017 – Mar 2019 | São Paulo, Brazil**

**Cloudera Cluster Implementation**
- Implemented and operated 3 Cloudera clusters (Data Lake, M2M, BI); optimized heavy Spark/Hive workloads, cutting processing time by **50%**; secured clusters with Kerberos (AD as KDC) and cross-realm trust.
- Integrated Hive/Impala with BI tools (SAS, QlikView, Alteryx), built the ingestion framework and monitoring scripts, and mentored/led 2 engineers.

**Nextel — Sustainment & ETL**
- Developed ETL ingestion, analyzed data with Beeline/Impala, extracted data via Sqoop, and sustained the production environment.

---

### Big Data Analyst — Vivo
**Jun 2017 – Sep 2017 | Brazil**

**Hadoop Migration & Sustainment**
- Hadoop 2.2 → 2.6 migration, PySpark ETL pipelines, HBase persistence, and Zookeeper-managed cluster high availability.

---

## OPEN-SOURCE PROJECTS (github.com/Pauloeduspbr)

- **medallion-data-lake** — production-ready Bronze/Silver/Gold template with Airflow, dbt, and Terraform (AWS + GCP), SCD Type 2 dimensions and 36 automated tests.
- **crypto-data-pipeline** — pipeline ingesting market data for 100 assets (CoinGecko API) with Airflow, PostgreSQL, and Docker; 7/7 automated data quality checks passing.
- **dune-analytics-queries** — 12 SQL queries analyzing large-scale on-chain datasets (Ethereum, Solana, DeFi, NFT).

---

## EDUCATION

- **Associate Degree in Big Data and Data Intelligence** — Anhembi Morumbi University | Expected 2026
- **Artificial Intelligence** (in progress) — FMU
- **Bachelor of Science in Information Systems** — UNIP | 2006

---

## CERTIFICATIONS

- Red Hat Certified System Administrator (RHCSA)
- Big Data Engineering — Garre Training (160h)

---

## LANGUAGES

- **Portuguese:** Native
- **English:** Upper-Intermediate (B2) — fluent technical reading and writing
