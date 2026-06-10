# Paulo Eduardo dos Santos

**Senior Data Engineer**

Sao Paulo, Brazil — Remote (UTC-3, LATAM) | paulo_eduardosp@yahoo.com.br | +55 11 91526-7337
LinkedIn: linkedin.com/in/paulo--eduardo | GitHub: github.com/Pauloeduspbr

---

## Professional Summary

Senior Data Engineer with 9+ years designing, building, and maintaining robust data pipelines that integrate product, transactional, and financial data at scale for banking, payments, and e-commerce platforms. Strong SQL and Python, with hands-on production experience across cloud data warehouses (Snowflake, BigQuery, Redshift), transformation and orchestration with dbt and Airflow, and big data processing with Apache Spark, AWS EMR, and S3. Embeds data quality, security, and data governance into every pipeline (PII/LGPD-compliant healthcare and financial data), deploys infrastructure as code with Terraform, and automates CI/CD workflows. Builder of public open-source data projects, including blockchain data analytics on Ethereum and Solana.

---

## Skills

- **Languages:** SQL (advanced), Python (advanced), PySpark, Shell Script
- **Transformation & Orchestration:** dbt, Apache Airflow, ETL/ELT design, CDC
- **Cloud Warehouses:** Snowflake, BigQuery, Redshift
- **Big Data & Distributed Processing:** Apache Spark, AWS EMR / EMR Serverless, S3, Athena, Trino, Kafka
- **Data Modeling:** dimensional modeling (star schema, Kimball), data warehouse design, Medallion/lakehouse (Delta Lake, Apache Iceberg)
- **Data Quality & Data Governance:** data quality frameworks (cross-origin validations, automated dbt tests), data governance and metadata management with data catalogs (AWS Glue Catalog, Unity Catalog), PII/LGPD compliance, HashiCorp Vault, AWS KMS
- **Infrastructure as Code & CI/CD:** Terraform, Docker, Kubernetes, Git, CI/CD automation
- **Reporting:** Power BI, QlikSense, Grafana dashboards

---

## Open-Source Projects (github.com/Pauloeduspbr)

- **dune-analytics-queries** — 12 SQL queries analyzing blockchain data on Dune: DeFi protocol metrics, NFT markets, Ethereum and Solana activity, cross-chain comparisons.
- **crypto-data-pipeline** — production-style pipeline ingesting market data for 100 crypto assets (CoinGecko API) with Airflow, PostgreSQL, and Docker; 7/7 automated data quality checks passing, 1.74s end-to-end execution.
- **medallion-data-lake** — production-ready Bronze/Silver/Gold template with Airflow, dbt, and Terraform (AWS + GCP), SCD Type 2 dimensions and 36 automated tests.

---

## Work Experience

### Data Engineer — BRQ (Clients: RD Saude, Itau)
**Jul 2025 – Jun 2026 | Remote, Brazil**

- Built a healthcare data lake on Apache Iceberg/S3 (Medallion architecture) integrating 3 healthcare platforms (Amplimed, HAOC, Vitat) plus CRM, scheduling, and clinical event sources into a Customer 360 analytical model served through Trino, Athena, and Redshift.
- Developed PySpark/SparkSQL pipelines orchestrated by Airflow DAGs on Spark-over-Kubernetes, with automated YAML manifest generation in Python.
- Embedded data quality (cross-origin validations, light checks), observability (custom log handlers, Spark metrics, AWS SNS/Step Functions alerts), and a YAML-versioned data catalog into all pipelines.
- Implemented PII/LGPD data security and governance with HashiCorp Vault, AWS KMS, and Fernet encryption for sensitive health data.
- For Itau: built ETL pipelines with EMR Serverless and Glue Studio, optimized SQL for performance, and implemented data quality processes supporting A/B test analysis.

### Senior Big Data Specialist / Data Engineer — Stefanini (Clients: Banco do Brasil, Cielo, AmericaNet, Itau, Brasildev)
**Jun 2023 – Jun 2025 | Sao Paulo, Brazil**

- Architected dbt models in Snowflake for financial reporting with automated data quality tests and versioned transformations (Banco do Brasil).
- Sustained a production Big Data environment processing millions of daily financial transactions at 99.9% uptime SLA; built a Python automation framework cutting maintenance effort by 40%.
- Led multi-cloud migration of payment data (Cielo): Oracle to AWS, Azure, and GCP, including data mapping and migration to BigQuery and analytical data migration to Snowflake with dbt dimensional models feeding Power BI dashboards.
- Built ELT pipelines with dbt in Snowflake exposing terabyte-scale curated data through Python REST APIs, reducing manual intervention by 70% via automation (AmericaNet).
- Refactored legacy SQL into Parquet/PySpark jobs for Itau, achieving 60% storage reduction, and deployed the data catalog with AWS Glue.
- Built an AWS data lake (Bronze/Silver/Gold) with governance via Lake Formation and infrastructure automated with Terraform; Python ingestion engine integrated with Salesforce.

### Senior Data Engineer — Natura &Co
**Feb 2022 – Jun 2023 | Sao Paulo, Brazil**

- Modernized the corporate data lake for global e-commerce: led Parquet-to-Delta Lake migration with ACID transactions and schema evolution.
- Designed dimensional models (customer journey, cohort analysis) integrating web analytics, transactional, and CRM sources; built dbt models in Snowflake with data quality tests.
- Implemented complex Airflow DAGs with dynamic dependencies and EMR Serverless pipelines; incremental CDC loads integrated with BI via Redshift Spectrum.

### Earlier Experience (Jun 2017 – Feb 2022)

- **Enel — Data Engineer (May 2021 – Feb 2022):** migrated the corporate data warehouse from Impala to Redshift (Talend); QlikSense dashboards, query optimization, and business team training.
- **Banco do Nordeste — Big Data Solutions Architect (Jan 2021 – May 2021):** designed a corporate data lake (raw/stage/analytics) for banking credit systems; Cassandra, Dremio, DataStage.
- **Hospital Sirio-Libanes — Big Data Architect/Engineer (Mar 2019 – Dec 2020):** Airflow-orchestrated ingestion pipelines on AWS (S3, Athena, EMR, Kinesis, Lambda), Docker/Kubernetes, SSO with AWS Cognito + Azure AD.
- **Claro Brasil — Big Data Technical Lead (Sep 2017 – Mar 2019):** implemented 3 Cloudera clusters, cut processing time by 50%, mentored a team of 2 engineers.
- **Vivo — Big Data Analyst (Jun 2017 – Sep 2017):** Hadoop 2.2-to-2.6 migration, PySpark pipelines, Zookeeper cluster HA.

---

## Education

- **Associate Degree, Big Data and Data Intelligence** — Anhembi Morumbi University (expected 2026)
- **Artificial Intelligence** (in progress) — FMU
- **BSc, Information Systems** — UNIP (2006)

---

## Certifications

- Red Hat Certified System Administrator (RHCSA)
- Big Data Engineering — Garre Training (160h)

---

## Languages

- Portuguese (native) | English: Upper-Intermediate (B2) — fluent technical reading and writing
