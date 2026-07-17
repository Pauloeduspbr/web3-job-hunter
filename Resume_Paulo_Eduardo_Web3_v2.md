# Paulo Eduardo dos Santos

**Senior Data Engineer | Cloud & Big Data Specialist | FinTech & Digital Assets**

Americana — São Paulo, Brazil (Open to Remote) | +55 11 91526-7337 | paulo_eduardosp@yahoo.com.br
LinkedIn: linkedin.com/in/paulo--eduardo | GitHub: github.com/Pauloeduspbr

---

## PROFESSIONAL SUMMARY

Senior Data Engineer with 9 years of experience designing and operating large-scale data platforms for banks, payments, telecom, healthcare, and e-commerce organizations that process millions of daily transactions. Specialized in Data Lake / Lakehouse and Data Warehouse architecture (Medallion Bronze/Silver/Gold, Star/Snowflake schemas), ETL/ELT pipeline design, data governance and data quality, and multi-cloud migrations across AWS, Azure, and GCP.

Hands-on across the modern data stack — Python, SQL, PySpark/Spark, Airflow, dbt, Kafka, Snowflake, and Iceberg/Delta Lake — with proven results: 99.9% uptime SLA, 60% storage reduction, 50% faster processing, and 70% less manual operation. Builder of public open-source blockchain-data projects (Ethereum, Solana, DeFi) bridging strong enterprise data engineering with Web3/FinTech.

---

## TECHNICAL SKILLS

**Languages:** Python (advanced), SQL (advanced), PySpark, Shell Script, Scala

**Cloud:** AWS (S3, EMR / EMR Serverless, Glue, Athena, Redshift, Lambda, Kinesis, Lake Formation, DMS, Step Functions, KMS, CloudWatch) · Azure (Data Lake, Databricks, Data Factory, Synapse, Unity Catalog, Fabric) · GCP (BigQuery, Dataproc)

**Processing & Orchestration:** Apache Spark, PySpark, SparkSQL, Apache Airflow, Apache NiFi, dbt, Kafka, Talend, DataStage, SSIS, Informatica PowerCenter/BDM, Sqoop, Flume

**Architecture:** Big Data (Hadoop/Spark ecosystems), Data Lake & Lakehouse (Bronze/Silver/Gold), Data Warehouse (Star/Snowflake schema), Dimensional Modeling, CDC, Event-Driven, Cloud Migration (on-prem → cloud)

**Lakehouse & Formats:** Delta Lake, Apache Iceberg, Apache Hudi, Parquet

**Databases:** Snowflake, SQL Server, Oracle, Teradata, PostgreSQL, MySQL, Redshift, MongoDB, Cassandra, HBase, DynamoDB

**Governance & Quality:** Data Quality frameworks, Data Governance, Data Catalog (AWS Glue, Unity Catalog), PII/LGPD compliance, HashiCorp Vault, AWS KMS, Fernet encryption

**DevOps & IaC:** Docker, Kubernetes, Terraform, Ansible, CI/CD, Git

**Visualization:** Power BI, QlikSense, Tableau, Spotfire, MicroStrategy, OBIEE, Grafana

**Methodologies:** Agile for Analytics (Scrum, SAFe), requirements gathering for analytics projects

---

## KEY ACHIEVEMENTS

- Sustained a **99.9% uptime SLA** for Banco do Brasil's Big Data environment processing millions of daily transactions
- Cut maintenance time by **40%** via a reusable Python automation framework
- Achieved **60% storage reduction** migrating legacy SQL tables to Parquet/Delta Lake
- Reduced processing time by **50%** through Big Data cluster optimization at Claro Brasil
- Reduced manual intervention by **70%** through Azure Automation pipelines
- Led **multi-cloud migration** (Oracle → AWS + Azure + GCP) of Cielo payment data
- Delivered a healthcare Data Lake on Apache Iceberg with full **PII/LGPD governance** (Vault, KMS, Fernet)

---

## PROFESSIONAL EXPERIENCE

### Data Engineer — BRQ
**Jul 2025 – Present | Remote, Brazil**

**RD Saúde — Healthcare Data Lake (Customer 360)**
- Built a healthcare Data Lake with Medallion architecture (Bronze/Silver/Gold) on Apache Iceberg over S3, supporting electronic health records, scheduling, vaccines, medication, prescriptions, and tele-consultation use cases (Amplimed, HAOC, Vitat).
- Developed PySpark/SparkSQL pipelines for large-scale ingestion, transformation, and consolidation of clinical data, with support for Apache Iceberg and Apache Hudi.
- Orchestrated Airflow DAGs integrated with Spark on Kubernetes, with automated YAML manifest generation through Python builders.
- Modeled the Customer 360 analytical table integrating multiple sources (CRM, scheduling, events, interests) served via Trino, Athena, and Redshift.
- Implemented an in-house Data Quality framework (cross-origin validations, light checks, DLS validations) and a YAML-versioned data catalog.
- Secured sensitive health data (PII/LGPD) with HashiCorp Vault, AWS KMS, and Fernet encryption, including decrypt pipelines in landing.
- Integrated API ingestion (Amplimed, HAOC, Precifica) with async S3 clients and evolving schema handling (JSON/Parquet/Iceberg).
- Built end-to-end observability (custom log handlers, Spark metrics, exception tracking, Iceberg table comments) integrated with AWS SNS and Step Functions; maintained Docker containers (dev/qa/prod) for PySpark and Python K8s jobs.

**Itaú — Modernization & Analytics**
- Developed ETL pipelines using EMR Serverless and Glue Studio; optimized SQL queries for performance and implemented data quality processes.
- Performed A/B test analysis and developed metric-improvement analyses and hypothesis validation.

---

### Senior Big Data Specialist / Data Engineer — Stefanini
**Jun 2023 – Jun 2025 | São Paulo, Brazil**

**Banco do Brasil — Big Data Environment Sustainment**
- Sustained and optimized a production Cloudera/Hortonworks cluster, ensuring **99.9% uptime SLA**.
- Developed Python and Shell automation for operational processes; built Jupyter notebooks for exploratory analysis and Ansible jobs for infrastructure management.
- Optimized Hive queries and maintained HDFS structures; built dbt models in Snowflake for financial reporting with data quality tests and versioned transformations.

**AmericaNet — APIs & Data Processing**
- Developed a RESTful API in Python Flask to expose processed data; implemented complex transformations with SparkSQL in Databricks.
- Automated processes with Azure Automation and built data pipelines with error handling and logging; built dbt/Snowflake ELT models with integrity validations and Unity Catalog.

**Cielo — Dashboard Analytics**
- Analyzed and documented legacy Oracle procedures; developed PySpark scripts for high-volume processing and Athena external tables over S3 with partitioning.
- Migrated analytical data to Snowflake with dbt dimensional modeling supporting Power BI dashboards.

**Itaú — ETL Process Refactoring**
- Refactored legacy SQL tables to Parquet and converted stored procedures to PySpark jobs, achieving **60% storage reduction**.
- Built a data catalog with AWS Glue, implemented data quality processes, and produced detailed technical documentation of all migrated processes.

**DirectLog — Geolocation System**
- Built a pipeline capturing latitude/longitude via the Google Maps API and Airflow DAGs for batch address processing.
- Implemented an authenticated SFTP web interface, EC2 hosting, and a caching layer to optimize API calls.

**Brasildev — AWS Data Lake**
- Built a layered Data Lake (Bronze/Silver/Gold) with a data catalog and governance; created a Python ingestion engine with Salesforce integration.
- Configured security/access policies with Lake Formation and automated infrastructure with Terraform.

---

### Senior Data Engineer — Natura & Co
**Feb 2022 – Jun 2023 | São Paulo, Brazil**

**E-commerce Pipeline**
- Modeled dimensional data for e-commerce analytics; developed ETL pipelines with EMR Serverless and Airflow DAGs for orchestration.
- Built Delta Lake structures for data versioning and incremental load processes; integrated with BI via Redshift.
- Built dbt models in Snowflake for customer-behavior analysis with data quality tests.

**Cielo — Cloud Migration & Modernization**
- Analyzed Oracle data structures and mapped them to BigQuery; migrated legacy data to Azure Blob Storage and built pipelines in Azure Data Factory with Unity Catalog cataloging.
- Converted complex SQL logic to distributed processing; developed PySpark and SparkSQL on Databricks; monitored spark-submit jobs.

**JBS — Data Pipeline Modernization**
- Provided technical leadership for a team of engineers and developers.
- Implemented a high-availability NiFi cluster integrated with Active Directory; configured an Application Load Balancer and built NiFi flows for SAP ingestion and S3↔Redshift movement.

---

### Data Engineer — Enel
**May 2021 – Feb 2022 | Brazil**

**Data Warehouse Migration**
- Built a migration pipeline with Talend Open Studio moving data from Impala to Redshift.
- Created QlikSense dashboards connected to Redshift, documented existing ETL processes, optimized queries, and trained business teams on the new tooling.

---

### Big Data Solutions Architect — Banco do Nordeste
**Jan 2021 – May 2021 | Brazil**

**Corporate Data Lake**
- Designed a Data Lake architecture with raw, stage, and analytics zones; implemented an unmanaged Hadoop cluster and configured Dremio for the analytics layer.
- Planned a NoSQL structure with Cassandra for a credit system; integrated legacy systems via DataStage and produced architecture documentation.

**Bradesco — Data Ingestion Framework**
- Updated ingestion-framework scripts for Hive and HBase tables; developed shell automation and integrated with the IBM IWS scheduler.
- Connected to Teradata for extraction and optimized load/transformation processes.

---

### Big Data Architect / Engineer — Hospital Sírio-Libanês
**Mar 2019 – Dec 2020 | São Paulo, Brazil**

**Hospital Analytics Platform**
- Analyzed and ingested hospital data from multiple sources; installed and configured Airflow for orchestration and developed ETL DAGs.
- Implemented Docker containers integrated with Airflow, configured Kubernetes for scalability, integrated AWS Cognito with Azure AD for SSO, and set up a CloudWatch→Elasticsearch pipeline via Lambda.

**Raízen — Data Ingestion Framework**
- Surveyed the data-pipeline architecture and analyzed Azure Data Lake, Databricks, and Power BI; documented SAP integration via SSIS Theobald.

**Dell EMC (Client: Fleury) — Consulting & Training**
- Analyzed data and sustained a Hortonworks environment; configured security with Kerberos/Ranger and AD integration.
- Developed monitoring scripts for Oozie jobs, built Grafana monitoring dashboards, and delivered operational training to the client team.

---

### Big Data Technical Lead — Claro Brasil
**Sep 2017 – Mar 2019 | São Paulo, Brazil**

**Cloudera Cluster Implementation**
- Installed and configured 3 Cloudera clusters for distinct projects (Data Lake, M2M, BI); implemented Kerberos with AD as KDC and cross-realm trust between clusters in different domains.
- Integrated Hive/Impala with BI tools (SAS, QlikView, Alteryx), built a data ingestion framework and monitoring/sustainment scripts, and integrated Informatica BDM for ETL — cutting processing time by **50%**. Mentored and led 2 engineers.

**Nextel — Sustainment & ETL**
- Developed ETL ingestion processes, analyzed data with Beeline/Impala, extracted data via Sqoop from relational sources, gathered functional requirements, and sustained the production environment.

---

### Big Data Analyst — Vivo
**Jun 2017 – Sep 2017 | Brazil**

**Hadoop Migration & Sustainment**
- Built ETL ingestion processes, analyzed data with Hive and Python, migrated Hadoop 2.2 → 2.6, persisted data in HBase, and managed the cluster with Zookeeper.

---

## EDUCATION

- **Associate Degree in Big Data and Data Intelligence** — Anhembi Morumbi University | Expected 2026
- **Artificial Intelligence** (in progress) — FMU
- **Bachelor of Science in Information Systems** — UNIP | 2006

---

## CERTIFICATIONS

- Big Data Engineering — Garre Training (160h) | 2014
- Oracle Business Intelligence Suite — Garre Training (80h) | 2011
- Red Hat Certified System Administrator (RHCSA) — RedHat | 2008
- Cisco Certified Network Associate (CCNA) — IBTA | 2007
- Microsoft Certified Systems Engineer — Impacta | 2004

---

## OPEN-SOURCE PROJECTS (github.com/Pauloeduspbr)

- **dune-analytics-queries** — 12 SQL queries on Dune analyzing blockchain data: DeFi protocol metrics, NFT markets, Ethereum and Solana activity, cross-chain comparisons.
- **crypto-data-pipeline** — production-style pipeline ingesting market data for 100 crypto assets (CoinGecko API) with Airflow, PostgreSQL, and Docker; 7/7 automated data quality checks passing.
- **medallion-data-lake** — production-ready Bronze/Silver/Gold template with Airflow, dbt, and Terraform (AWS + GCP), SCD Type 2 dimensions and 36 automated tests.

---

## LANGUAGES

- **Portuguese:** Native
- **English:** Upper-Intermediate (B2) — fluent technical reading and writing
