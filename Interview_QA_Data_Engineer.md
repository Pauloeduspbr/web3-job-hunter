# Interview Preparation — Data Engineer (Crypto/FinTech)

**Candidate:** Paulo Eduardo dos Santos
**Target Companies:** BCB Group, Zinnia, and similar crypto/FinTech firms
**Profile:** Senior Data Engineer | 9 Years Experience | Python, SQL, AWS/Azure/GCP, Airflow, dbt, Spark, Kafka, Delta Lake

---

## 1. Technical Questions (15 Questions with Answers)

---

### Q1. How do you approach SQL query optimization, and can you give an example of using window functions to solve a real problem?

**A:** I start by analyzing the execution plan to identify full table scans, missing indexes, and expensive joins. At Banco do Brasil, I optimized Hive queries on financial transaction data by introducing partitioning by date and bucketing by account ID, which dramatically reduced scan volume. I regularly use window functions like `ROW_NUMBER()`, `LAG()`, and `SUM() OVER()` to handle deduplication, running balances, and change detection without self-joins. For instance, at Itau I used `LAG()` to detect account balance changes across daily snapshots, replacing a costly self-join that was timing out on millions of rows. The key is always to filter early, push predicates down, and let the optimizer work with partitioned data.

---

### Q2. Explain the difference between CTEs and subqueries. When do you prefer one over the other?

**A:** CTEs (Common Table Expressions) improve readability and allow recursive queries, while subqueries can sometimes be inlined by the optimizer more aggressively. I prefer CTEs when building layered transformations — for example, in dbt models at Banco do Brasil, I structured financial reporting queries as chains of CTEs (staging, deduplication, aggregation, final select) to make them self-documenting and testable. I use subqueries when I need a one-off filter or when the optimizer in engines like Redshift or BigQuery handles them more efficiently. In Hive and Spark SQL, CTEs are especially useful because the optimizer rewrites them internally, so the readability advantage comes at no performance cost.

---

### Q3. How do you design an ETL/ELT pipeline from scratch? Walk me through your approach.

**A:** I follow a layered approach aligned with the Medallion Architecture. First, I define the source contracts and ingestion method — batch via Airflow or streaming via Kafka. At Natura, I built the corporate Data Lake from scratch: the Bronze layer captured raw data from Web Analytics, CRM, and transactional systems using CDC and batch extractions into S3 as Parquet. The Silver layer applied deduplication, schema enforcement, and business key standardization using PySpark on EMR Serverless. The Gold layer served dimensional models for cohort analysis and BI via Redshift Spectrum. Throughout, I use dbt for transformation logic and Airflow for orchestration, with data quality checks at each layer boundary. The critical design decisions are idempotency, schema evolution handling, and clear lineage.

---

### Q4. Describe the Medallion Architecture (Bronze/Silver/Gold). How have you implemented it?

**A:** Bronze is the raw ingestion layer — append-only, schema-on-read, preserving the source exactly as received. Silver is the cleansed and conformed layer — deduplicated, typed, null-handled, and aligned to a common business model. Gold is the consumption layer — aggregated, denormalized, and optimized for analytics or reporting. At Natura, I led the Parquet-to-Delta Lake migration implementing this architecture with ACID transactions and schema evolution. Bronze stored raw JSON/CSV from multiple e-commerce sources in S3. Silver applied PySpark transformations with data quality assertions. Gold served dimensional models for customer journey analysis. At Banco do Nordeste, I designed an analogous Raw/Stage/Analytics zone architecture for banking credit data. The key benefit is isolation — a schema change in the source only breaks Bronze, not downstream consumers.

---

### Q5. How do you handle DAG design and failure recovery in Apache Airflow?

**A:** I design DAGs to be idempotent and atomic — every task can be safely retried without side effects. At Natura, I built complex Airflow DAGs with dynamic task dependencies using task groups and the TaskFlow API, orchestrating EMR Serverless jobs. For failure handling, I implement automatic retries with exponential backoff, SLA alerts via Slack/email, and dead-letter patterns for bad records. I use `on_failure_callback` to trigger PagerDuty alerts and `trigger_rule="all_done"` for cleanup tasks that must run regardless of upstream status. At Hospital Sirio-Libanes, I built Airflow pipelines that extracted from Oracle, transferred to S3, and converted formats — each step idempotent so that a retry at any point would not produce duplicates. Best practices I follow: short-lived tasks, XCom only for metadata (never data), sensors with timeouts, and separate DAGs for ingestion versus transformation.

---

### Q6. Explain dbt incremental models and snapshots. When do you use each?

**A:** Incremental models process only new or changed records since the last run, using a `unique_key` and an `is_incremental()` block to filter. I use them for large fact tables where full refreshes are impractical. At Banco do Brasil, I built incremental dbt models in Snowflake for daily financial transaction data — each run processed only the previous day's records using a `loaded_at` timestamp, reducing processing time from hours to minutes. Snapshots capture slowly changing dimensions (SCD Type 2) by tracking row-level changes over time with `valid_from` and `valid_to` columns. I used snapshots to track account status changes and customer attribute history for regulatory audit trails. The rule of thumb: incremental for append-heavy fact tables, snapshots for dimension tables where you need historical state. Both require careful handling of late-arriving data — I typically add a lookback window of 2-3 days to incremental models.

---

### Q7. How do you test and ensure quality in Python-based data pipelines?

**A:** I use a layered testing strategy: unit tests with pytest for transformation functions, integration tests against sample datasets, and data quality assertions in production. At Itau, I implemented data quality frameworks with A/B testing analysis for business hypothesis validation. For PySpark code, I write unit tests using small local DataFrames to validate transformation logic, then integration tests against a staging environment. I use Great Expectations or dbt tests for production data quality — checking uniqueness, not-null constraints, referential integrity, and statistical distribution anomalies. At Banco do Brasil, every dbt model had automated `unique`, `not_null`, and custom schema tests that ran before data was promoted from Silver to Gold. I also build monitoring dashboards in Grafana that track record counts, null rates, and freshness so we catch silent failures.

---

### Q8. Compare AWS Glue, EMR, and Athena. When do you choose each?

**A:** AWS Glue is best for serverless, catalog-driven ETL — I used Glue Studio at Itau for building visual ETL jobs and Glue Crawlers for automatic schema discovery and data catalog management. EMR (especially EMR Serverless) is my choice for heavy PySpark workloads that need fine-grained cluster control — at Natura, I ran complex Delta Lake transformations on EMR Serverless for cost efficiency, paying only for compute time. Athena is ideal for ad-hoc queries and lightweight analytics directly on S3 — at Cielo, I created Athena external tables with S3 partitioning for the payment data migration, enabling analysts to query migrated data immediately without loading it into a warehouse. The decision tree: Glue for catalog and simple ETL, EMR for heavy Spark, Athena for interactive SQL on S3. When working with GCP, the equivalents are Dataproc (EMR), BigQuery (Athena + warehouse), and Data Catalog — at Cielo, I used BigQuery and Dataproc for the GCP leg of the multi-cloud migration.

---

### Q9. How do you implement Change Data Capture (CDC) in a data pipeline?

**A:** CDC captures row-level insert, update, and delete events from source databases, enabling near-real-time data synchronization without full table scans. At Cielo, I implemented CDC processes during the Oracle-to-cloud migration using AWS DMS (Database Migration Service) to stream changes from Oracle to S3, then processed them with PySpark to merge into Delta Lake tables using `MERGE INTO` operations. At Natura, I used CDC for incremental loads from transactional systems into the Data Lake — changes were captured as event streams, landed in Bronze as append-only logs, then applied in Silver using Delta Lake's merge capabilities with ACID guarantees. The key challenges are handling deletes (soft delete flags versus hard deletes), ordering events correctly when they arrive out of sequence, and managing schema changes in the source. I prefer log-based CDC (reading database transaction logs) over trigger-based or timestamp-based approaches because it has zero impact on source system performance.

---

### Q10. How do you handle schema evolution in production data pipelines?

**A:** Schema evolution is inevitable and must be planned for from day one. At Natura, when we migrated from Parquet to Delta Lake, one of the primary motivations was Delta's native schema evolution support — you can enable `mergeSchema` to automatically add new columns without breaking downstream consumers. My approach is defensive: Bronze accepts any schema (schema-on-read), Silver enforces a contract with explicit column mapping and type casting, and Gold models are versioned through dbt. When a source adds a column, it flows through Bronze automatically, I update the Silver transformation to map it, and downstream Gold models only change if the business needs the new field. At Cielo, during the multi-cloud migration, I dealt with schema differences between Oracle, AWS, and GCP — I built a metadata layer that tracked column mappings and type conversions across all three platforms. For breaking changes (column removals or type changes), I use dbt schema tests to catch failures early and communicate with upstream teams through data contracts.

---

### Q11. How would you design a real-time streaming pipeline using Kafka?

**A:** I design Kafka pipelines with a clear separation of concerns: producers publish raw events to topics, stream processors (Spark Structured Streaming or Kafka Streams) transform and enrich them, and consumers sink results to storage or serving layers. At Hospital Sirio-Libanes, I worked with AWS Kinesis (a Kafka-equivalent) for real-time data ingestion pipelines. For a crypto exchange scenario, I would set up Kafka topics partitioned by trading pair (e.g., BTC-USD, ETH-USD) to ensure ordering within each pair. The stream processor would apply windowed aggregations (VWAP, rolling volume), detect anomalies (wash trading, flash crashes), and enrich with reference data. I would use Schema Registry to enforce Avro or Protobuf schemas on producers, preventing schema drift from breaking consumers. The sink would write to both a real-time serving layer (Redis or DynamoDB for dashboards) and a Delta Lake table for historical analytics. Key design decisions: exactly-once semantics via idempotent producers and transactional consumers, dead-letter queues for poison messages, and consumer group management for horizontal scaling.

---

### Q12. What is your approach to data governance and access control?

**A:** I implement governance at multiple layers: catalog-level discovery, column-level access control, and audit logging. At my projects, I deployed AWS Lake Formation with granular access policies — defining which roles can read which columns and rows, enforcing PII masking for non-privileged users. I used AWS Glue Data Catalog as the central metadata repository, ensuring every table had descriptions, owners, and classification tags. At Banco do Nordeste, I designed the Data Lake architecture with separate Raw/Stage/Analytics zones, each with distinct IAM policies — data engineers had write access to all zones, analysts had read-only access to Analytics, and external consumers accessed only curated views. For dbt projects, I use role-based access in Snowflake with separate schemas for staging and production, and all transformations are version-controlled in Git. Compliance in financial environments means every data access must be logged, retention policies enforced, and sensitive fields (CPF, account numbers) masked or tokenized by default.

---

### Q13. How do you handle data versioning and reproducibility?

**A:** Reproducibility requires versioning at three levels: code (Git), data (Delta Lake or snapshot tables), and infrastructure (Terraform). At Natura, Delta Lake gave us time-travel capability — we could query any table as of any point in time, which was critical for debugging and audit. All dbt models were version-controlled in Git with CI/CD pipelines that ran tests before deploying to production. At Itau, I built data quality frameworks that logged every pipeline run's input/output row counts, schema fingerprints, and transformation hashes so we could trace any output back to its exact inputs and code version. For infrastructure, I advocate for Terraform (which I have used across projects) to version cloud resources — if an EMR cluster configuration changes, it is tracked and reviewable. The combination of Delta Lake time-travel, Git-versioned dbt models, and Terraform-managed infrastructure means I can reproduce any pipeline result from any historical point.

---

### Q14. Compare Data Mesh and centralized Data Lake approaches. When is each appropriate?

**A:** A centralized Data Lake works well when a single team can own the entire data platform and domains are tightly coupled — this was the case at Natura, where I built and managed the corporate Data Lake for the entire e-commerce operation. Data Mesh distributes ownership to domain teams, treating data as a product with self-serve infrastructure. It suits large organizations with many autonomous domains. At a company like Cielo, where payment, merchant, and fraud data belong to different business units, a mesh approach with shared standards would reduce bottlenecks. The key to Data Mesh is not just decentralization — it requires a strong self-serve platform (standardized Airflow templates, dbt project structures, CI/CD), federated governance (agreed-upon naming conventions, quality SLAs, and interoperability standards), and product thinking (every dataset has an owner, SLA, documentation, and quality metrics). In practice, I have seen hybrid approaches work best — a centralized platform team provides the infrastructure, while domain teams own their data products.

---

### Q15. How do you optimize PySpark jobs for performance?

**A:** The most impactful optimizations are: proper partitioning to avoid shuffles, broadcast joins for small dimension tables, columnar storage (Parquet/Delta), and avoiding UDFs in favor of native Spark functions. At Cielo, I wrote PySpark scripts for transactional Big Data — I partitioned data by transaction date and payment method, used `broadcast()` hints for merchant lookup tables, and configured `spark.sql.shuffle.partitions` based on data volume. At Claro Brasil, I achieved a 50% processing time reduction by right-sizing cluster configurations, tuning memory allocation (`spark.executor.memory`, `spark.driver.memory`), and eliminating unnecessary `collect()` calls that were pulling data to the driver. Other techniques I regularly use: caching intermediate DataFrames that are reused multiple times, using `repartition()` before writes to control output file sizes (avoiding small files problem), predicate pushdown by filtering early, and monitoring Spark UI to identify skewed partitions. At Itau, I refactored legacy stored procedures to PySpark jobs — the key was rethinking the logic from a set-based distributed perspective rather than a row-by-row procedural one.

---

## 2. Behavioral Questions (10 STAR-Format Answers)

---

### Q1. Tell me about a time you led a data migration project.

**Situation:** At Cielo, Brazil's largest payment processor, the company needed to migrate its payment transaction data infrastructure from legacy Oracle databases to a multi-cloud environment spanning AWS, Azure, and GCP.

**Task:** I was responsible for leading the technical execution of this migration, ensuring zero data loss, minimal downtime, and that all three cloud platforms received consistent, accurate data.

**Action:** I designed a phased migration strategy. First, I set up CDC pipelines using AWS DMS to stream changes from Oracle to S3, ensuring the source system was not impacted. Then I developed PySpark scripts to transform and load data into each cloud target — Athena external tables with S3 partitioning on AWS, Databricks on Azure, and BigQuery on GCP. I created reconciliation scripts that compared row counts, checksums, and sample records across all four systems (Oracle + three clouds) to validate completeness. I documented every mapping and transformation for audit purposes.

**Result:** The migration was completed successfully with full data integrity across all three cloud platforms. Analysts could immediately query data on their preferred platform, and the new architecture reduced storage costs through columnar formats while enabling the team to leverage cloud-native analytics tools that were not possible with Oracle alone.

---

### Q2. Describe a situation where a pipeline failed in production.

**Situation:** At Banco do Brasil, one of our critical Hive-based financial reporting pipelines began failing intermittently during peak processing hours, affecting downstream reports that had a strict SLA for regulatory submission.

**Task:** I needed to diagnose the root cause, restore the pipeline within the SLA window, and implement a permanent fix to prevent recurrence.

**Action:** I immediately checked Cloudera Manager metrics and identified that the cluster was experiencing memory pressure due to a recently added workload competing for YARN resources. As a short-term fix, I adjusted the pipeline's YARN queue priority and memory allocation to ensure it had dedicated resources during its critical window. Then I optimized the problematic Hive queries by introducing partition pruning and bucketing on the account ID column, reducing the data scanned by over 70%. I also added monitoring alerts in our Python automation framework to detect memory pressure early and trigger preemptive notifications.

**Result:** The pipeline was restored within the SLA window, and the optimizations reduced its execution time by roughly 40%. The monitoring alerts I added caught two similar situations in the following months before they impacted production, contributing to the team maintaining 99.9% uptime SLA on the Big Data environment.

---

### Q3. How do you handle conflicting priorities from stakeholders?

**Situation:** At Natura, the marketing team urgently needed customer cohort analysis data in the Gold layer for a major campaign launch, while the finance team required month-end reporting pipelines to be prioritized for board reporting — both with overlapping deadlines and shared infrastructure.

**Task:** I needed to deliver both workloads on time without degrading either team's output, using the same EMR Serverless cluster and Airflow instance.

**Action:** I scheduled a joint meeting with both stakeholders to understand their true deadlines and minimum viable deliverables. The finance team's hard deadline was 48 hours away; marketing's campaign launch was five days out. I proposed a phased approach: finance pipelines would run first during off-peak hours with dedicated EMR capacity, and I would build the marketing cohort models incrementally, delivering a partial dataset within 72 hours and the full dataset by day five. I communicated this plan transparently with clear milestones and set up Slack notifications for each completion step so both teams had real-time visibility.

**Result:** Both teams received their data on time. The finance reports shipped 12 hours before the board meeting, and the marketing cohort analysis was complete two days before the campaign launch. The joint meeting approach became a standard practice for priority conflicts on the team.

---

### Q4. Tell me about a time you optimized a slow process.

**Situation:** At Claro Brasil, the Big Data team was running three Cloudera clusters for telecom data processing, but batch jobs that should have completed in a few hours were taking 8-12 hours, delaying downstream analytics and reporting.

**Task:** As the Big Data Technical Lead, I was tasked with diagnosing the bottlenecks and reducing processing time significantly.

**Action:** I led a systematic performance audit across all three clusters. I discovered several issues: unbalanced data distribution causing hotspots on specific DataNodes, suboptimal YARN resource allocation leaving nodes underutilized, and Spark jobs using default configurations instead of being tuned for our workload. I rebalanced HDFS data across nodes, reconfigured YARN capacity scheduler to allocate resources proportionally, tuned Spark executor memory and parallelism settings, and rewrote several key PySpark jobs to use broadcast joins and proper partitioning strategies. I also implemented Grafana-based monitoring dashboards so the team could proactively detect performance degradation.

**Result:** We achieved a 50% reduction in processing time across the board. Jobs that previously took 10 hours completed in under 5. The Grafana monitoring system I built became the standard observability tool for the infrastructure team, and I mentored two junior engineers on performance tuning best practices.

---

### Q5. How do you ensure data quality in your pipelines?

**Situation:** At Banco do Brasil, financial reporting data had to meet strict accuracy and completeness standards for regulatory compliance. Any quality issues in transaction data could lead to incorrect reports submitted to the Central Bank.

**Task:** I needed to implement a comprehensive data quality framework that caught issues before they reached the Gold layer and provided audit trails for compliance.

**Action:** I implemented a multi-layer quality approach. In dbt models on Snowflake, I defined `unique`, `not_null`, and custom schema tests for every model — referential integrity checks between accounts and transactions, value range assertions for monetary amounts, and freshness tests ensuring data was not stale. I built a Python automation framework that ran reconciliation checks comparing record counts and aggregates between source systems and the Data Lake at every pipeline stage. For critical fields like transaction amounts and account balances, I added statistical anomaly detection that flagged records deviating more than three standard deviations from historical patterns. All test results were logged and dashboarded for the compliance team.

**Result:** The framework caught 15+ data quality issues in the first month alone — including a source system bug that was silently duplicating records — before any of them reached production reports. The 40% reduction in maintenance time from the automation framework was largely driven by replacing manual quality checks with automated ones. The compliance team reported increased confidence in the data, and the framework became a template for other teams.

---

### Q6. Tell me about a time you had to learn a new technology quickly.

**Situation:** At AmericaNet, the client's architecture was built on Azure Databricks and Snowflake with dbt — and they needed someone who could immediately contribute to building ELT pipelines. While I had deep experience with AWS and Spark, my hands-on Azure Databricks experience was limited at that point.

**Task:** I needed to become productive in Azure Databricks and the dbt-Snowflake ecosystem within the first two weeks of the engagement to meet project delivery timelines.

**Action:** I dedicated the first week to intensive self-study — working through Databricks documentation, building sample notebooks that replicated patterns I knew from EMR, and studying the dbt-Snowflake adapter's specific behaviors (materialization strategies, incremental model nuances). I leveraged my strong PySpark foundation to translate my existing knowledge to the Databricks context. I paired with the senior architect on the first few pull requests to absorb project conventions. By week two, I was independently building ELT pipelines and processing terabyte-scale data using SparkSQL in Databricks.

**Result:** I delivered the ELT pipelines on schedule, and the Azure Automation scripts I built reduced manual intervention by 70%. The client extended the engagement based on the quality of delivery. This experience also made me a more versatile multi-cloud engineer — I could now confidently work across AWS, Azure, and GCP.

---

### Q7. Describe a time you mentored or led a team.

**Situation:** At Claro Brasil, I was promoted to Big Data Technical Lead responsible for the telecom's data platform, managing a team of two data engineers while simultaneously handling architecture and hands-on development.

**Task:** I needed to grow the team's capabilities in Cloudera administration, PySpark development, and cluster performance tuning while delivering on aggressive project timelines.

**Action:** I established weekly knowledge-sharing sessions where I walked the team through real production issues — showing how I diagnosed the cluster performance problems, explaining the reasoning behind configuration changes, and letting them practice in a staging environment. I created runbooks for common operations and set up code review practices where I provided detailed feedback on PySpark optimization. I delegated increasingly complex tasks, starting with monitoring dashboard creation (Grafana) and progressing to independent pipeline development, providing guidance without taking over.

**Result:** Both engineers became self-sufficient in cluster management and PySpark development within four months. One of them independently resolved a critical HDFS replication issue during an on-call shift using the runbooks and diagnostic skills from our sessions. The team's velocity increased measurably, and the knowledge-sharing model was adopted by adjacent teams.

---

### Q8. Tell me about a time you had to push back on a technical decision.

**Situation:** At Natura, a stakeholder requested that we bypass the Silver layer and load raw data directly from Bronze into Gold-layer dimensional models to speed up delivery of a dashboard for an executive presentation.

**Task:** I needed to balance the urgency of the business request with the long-term integrity of the data architecture I had designed.

**Action:** I scheduled a 30-minute call with the stakeholder and demonstrated, with concrete examples, the risks: raw data contained duplicates, null values in key fields, and inconsistent date formats that would produce incorrect aggregations in the dashboard. I proposed a compromise — I would fast-track the Silver transformations for only the three specific source tables needed for the dashboard (instead of the full backlog), which I could complete in two days rather than the two weeks needed for the full Silver layer. This gave them clean, trustworthy data with minimal delay.

**Result:** The stakeholder agreed to the two-day timeline. The dashboard launched on time with accurate data, and the executive presentation went smoothly. More importantly, it established a precedent that data quality gates were non-negotiable, and subsequent requests followed the layered architecture by default.

---

### Q9. Describe a situation where you worked with cross-functional teams.

**Situation:** At Hospital Sirio-Libanes, I was building the data platform that needed to integrate data from clinical systems (Oracle databases), administrative systems, and external health data sources. This required close collaboration with IT security, clinical informatics, and hospital administration.

**Task:** I had to design pipelines that satisfied clinical data requirements, strict healthcare privacy regulations, and IT security policies — all while delivering on a timeline agreed upon with hospital administration.

**Action:** I held discovery sessions with each team to understand their constraints: IT security required SSO integration with Azure AD, clinical informatics needed specific data transformations for medical coding standards, and administration wanted self-service access to operational dashboards. I designed the architecture to address all requirements — implementing AWS Cognito + Azure AD for SSO, building Airflow pipelines that applied HIPAA-equivalent data masking during the Oracle-to-S3 extraction phase, and containerizing the entire platform with Docker and Kubernetes for security and portability. I created clear API contracts between components so each team could validate their requirements independently.

**Result:** The platform launched successfully with full SSO integration, compliant data handling, and automated pipelines running on schedule. The containerized architecture allowed the IT team to deploy in their secured environment without modifications. The clinical informatics team adopted the data platform for ongoing research analytics beyond the original project scope.

---

### Q10. Tell me about a time you delivered under a tight deadline.

**Situation:** At Itau, the bank's regulatory team discovered that legacy SQL stored procedures generating compliance reports were producing inconsistent results due to an upstream schema change. The corrected reports were due to the regulator within one week.

**Task:** I was brought in to refactor the legacy SQL to a modern, reliable format and ensure the reports were accurate — all within five business days.

**Action:** I immediately audited the legacy stored procedures to understand the full transformation logic, then mapped each one to equivalent PySpark jobs. Rather than a direct translation, I refactored them to read from Parquet files (which I converted from the legacy SQL tables, achieving 60% storage reduction in the process) and used the AWS Glue Data Catalog for schema management. I ran the new PySpark jobs in parallel with the legacy stored procedures for two days, comparing outputs row by row to validate accuracy. I worked with the regulatory team daily to show them reconciliation results and get sign-off on each transformation.

**Result:** The refactored pipelines were in production by day four, with day five used for final validation and documentation. The reports were submitted to the regulator on time with full accuracy. The Parquet conversion and Glue Catalog integration became the new standard for all subsequent ETL modernization efforts at the bank.

---

## 3. Crypto/FinTech Specific Questions (10 Questions with Answers)

---

### Q1. What do you know about blockchain data structures?

**A:** A blockchain is an append-only, cryptographically linked list of blocks. Each block contains a header (previous block hash, timestamp, nonce, Merkle root) and a body (list of transactions). Transactions themselves contain inputs (references to previous unspent outputs), outputs (amounts and recipient addresses), and metadata. The Merkle tree structure allows efficient verification of transaction inclusion without downloading the entire block. From a data engineering perspective, blockchain data is inherently immutable and event-sourced, which maps naturally to append-only Bronze layers and Delta Lake architectures I have built throughout my career. The challenge is that raw blockchain data is deeply nested and denormalized — a single Ethereum transaction can have dozens of internal calls and log events that need to be flattened for analytics.

---

### Q2. How would you design a pipeline to ingest transaction data from a blockchain?

**A:** I would use a node RPC endpoint or a third-party indexer (Alchemy, Infura, The Graph) to extract block and transaction data, either via polling (batch) or WebSocket subscriptions (streaming). For batch, an Airflow DAG would poll for new blocks at regular intervals, extract transactions, and land raw JSON in a Bronze layer on S3 or GCS. For real-time, Kafka would receive events from a WebSocket listener, and Spark Structured Streaming would process them. In Silver, I would flatten nested structures (separating transactions, logs, internal calls into distinct tables), apply data types, and deduplicate any reorgs (chain reorganizations where blocks are replaced). Gold would serve aggregated models — daily transaction volumes by address, token transfer summaries, and wallet balance snapshots. This follows the exact Medallion Architecture pattern I implemented at Natura and Banco do Nordeste, adapted for blockchain-specific concerns like reorg handling and gas fee parsing.

---

### Q3. What are the challenges of real-time crypto market data processing?

**A:** Crypto markets operate 24/7 across hundreds of exchanges with no market close, generating extremely high-frequency tick data. Key challenges include: volume (millions of price updates per second across all pairs and exchanges), latency sensitivity (arbitrage strategies require sub-millisecond processing), data inconsistency (each exchange has its own API format, rate limits, and uptime), and price discrepancy (the same asset can trade at different prices across exchanges). From a data engineering perspective, you need a streaming architecture — Kafka for ingestion with partitioning by exchange and trading pair, Spark Structured Streaming or Flink for windowed aggregations (VWAP, OHLCV candles), and a low-latency serving layer (Redis, TimescaleDB). My experience building pipelines that process millions of daily transactions at Banco do Brasil with 99.9% uptime SLA directly applies — the pattern is the same, just with higher velocity and 24/7 operational requirements.

---

### Q4. How do you ensure data compliance in a regulated financial environment?

**A:** Compliance requires controls at every layer: access, lineage, quality, and auditability. In my work with Brazilian financial institutions (Banco do Brasil, Itau, Cielo), I operated under Central Bank of Brazil regulations that require strict data governance. Practically, this means: column-level access control (I used AWS Lake Formation to enforce who can see sensitive fields like account numbers and CPF/tax IDs), full audit logging of all data access and transformations, data retention policies enforced through automated lifecycle rules on S3, and data quality gates that prevent bad data from reaching regulatory reports. For crypto companies like BCB Group operating under FCA or similar regulations, the principles are identical — you need to demonstrate to regulators that you know where every piece of data came from, who accessed it, how it was transformed, and that it meets accuracy standards. I would implement this through a combination of dbt lineage, Delta Lake time-travel for point-in-time auditability, and centralized access control.

---

### Q5. What is your experience with regulatory reporting?

**A:** At Banco do Brasil, the data I managed directly fed regulatory reports submitted to the Central Bank of Brazil — financial transaction data with strict accuracy, completeness, and timeliness requirements. I built dbt models in Snowflake specifically for financial reporting, with automated quality tests that validated every report before submission. At Itau, I refactored legacy reporting stored procedures to PySpark jobs under a one-week regulatory deadline, running parallel validation to ensure the new pipelines produced identical results. The key principles I bring are: deterministic transformations (same input always produces the same output), reconciliation at every stage (source counts match target counts), version-controlled logic (every report formula is in Git and auditable), and clear documentation of business rules. For crypto regulatory reporting (SAR filings, transaction monitoring reports, balance attestations), I would apply the same rigor — with additional attention to blockchain-specific requirements like wallet attribution and cross-chain transaction tracking.

---

### Q6. How would you design a data warehouse for a crypto exchange?

**A:** I would design it around key business entities: Users, Wallets, Orders, Trades, Deposits, Withdrawals, and Market Data. The fact tables would be `fact_trades` (every executed trade with price, quantity, fees, timestamps), `fact_deposits_withdrawals` (on-chain and fiat movements), and `fact_order_events` (order lifecycle from placement to fill/cancel). Dimension tables would include `dim_users` (with KYC status), `dim_assets` (token metadata), `dim_markets` (trading pairs), and `dim_time`. I would use a Medallion Architecture: Bronze ingests raw API events and blockchain data, Silver normalizes and deduplicates (handling order book snapshots, trade matching), and Gold serves the dimensional model. For the technology stack, I would use BigQuery or Snowflake as the warehouse, dbt for transformation logic, and Airflow for orchestration — the same stack I used at Banco do Brasil and Natura. Critical considerations: real-time balance calculation (using running aggregations), cross-chain asset tracking, and separate schemas for internal analytics versus regulatory reporting.

---

### Q7. What is the difference between on-chain and off-chain data?

**A:** On-chain data is everything recorded on the blockchain itself — transactions, smart contract state, token transfers, block metadata, gas fees. It is immutable, publicly verifiable, and the source of truth for asset movements. Off-chain data is everything else — user profiles, KYC documents, fiat banking transactions, customer support tickets, internal order books, and application logs. For a crypto company, a complete data picture requires joining both: an on-chain deposit transaction needs to be linked to an off-chain user account, and a fiat withdrawal (off-chain banking event) needs to be reconciled against the exchange's internal ledger. The data engineering challenge is maintaining referential integrity between these two worlds — blockchain addresses must be reliably mapped to internal user IDs, timestamps must be normalized (block timestamps versus server timestamps), and the pipeline must handle blockchain-specific events like reorgs that can retroactively invalidate on-chain data. My experience integrating diverse data sources (Web Analytics, CRM, transactional databases) at Natura directly translates — the pattern of ingesting from heterogeneous sources, normalizing in Silver, and joining in Gold is the same.

---

### Q8. How would you handle a schema change in a high-volume payment processing pipeline?

**A:** In high-volume payment processing, schema changes must be handled with zero downtime and backward compatibility. At Cielo, I dealt with exactly this during the Oracle-to-cloud migration — source schemas evolved while the migration was in progress. My approach: first, the Bronze layer accepts any schema change automatically (schema-on-read with Parquet/Delta). Second, the Silver layer transformation has explicit column mapping — new columns are added with defaults, removed columns are handled gracefully. Third, I use Delta Lake's `mergeSchema` option for additive changes (new columns) and versioned transformations for breaking changes (type changes, column renames). For a real-time payment pipeline on Kafka, I would enforce Schema Registry with backward-compatible Avro schemas — producers can add optional fields but cannot remove or change existing ones without a coordinated migration. If a breaking change is unavoidable, I use a blue-green deployment pattern: deploy the new pipeline version reading from a new topic, validate output, then switch consumers — the same approach I used when refactoring stored procedures to PySpark at Itau.

---

### Q9. What data quality challenges are unique to financial/crypto data?

**A:** Financial and crypto data have several unique quality challenges beyond typical data engineering concerns. First, precision — monetary amounts must use exact decimal types (never floating point), and rounding rules vary by currency and jurisdiction. Second, reconciliation — every transaction has two sides, and your internal ledger must balance to the penny against external sources (bank statements, blockchain explorers, exchange APIs). Third, timeliness — regulatory reporting has hard deadlines, and stale data can mean compliance violations. Fourth, crypto-specific issues include: blockchain reorgs that invalidate previously confirmed transactions, token precision (ERC-20 tokens have variable decimal places), price manipulation that creates outliers in market data, and the 24/7 nature that eliminates natural batch windows. At Banco do Brasil, I built statistical anomaly detection for financial transaction amounts. For crypto, this extends to detecting wash trading, flash loan artifacts, and sandwich attacks in the data. The key is making these quality checks automated, fast, and integrated into the pipeline — not a separate manual process.

---

### Q10. How would you approach building a KYC/AML data pipeline?

**A:** A KYC (Know Your Customer) / AML (Anti-Money Laundering) pipeline needs to ingest identity verification data, transaction history, and external watchlists, then produce risk scores and suspicious activity alerts. I would design it in three layers: ingestion (customer onboarding events, ID verification results from providers like Jumio or Onfido, transaction events from the core platform, and sanctions/PEP lists from external sources), processing (entity resolution to link identities across data sources, transaction pattern analysis using windowed aggregations for unusual volume or velocity, network analysis to detect related accounts, and matching against sanctions lists), and output (risk scores per customer, SAR filing candidates, and audit-ready transaction histories). The technology would mirror what I have built in banking: Airflow for orchestration, PySpark for the heavy pattern analysis, dbt for the structured transformation logic, and a serving layer for compliance analysts. At Banco do Brasil and Itau, the data I managed was subject to similar Central Bank regulations. The crypto-specific addition is on-chain analytics — tracing wallet relationships through blockchain graph analysis and flagging interactions with known illicit addresses using services like Chainalysis or Elliptic.

---

## 4. Questions to Ask the Interviewer (10 Smart Questions)

---

### Q1. Architecture and Scale

"Can you describe the current data architecture — what does the stack look like from ingestion through to the analytics layer? I am curious about where you are on the journey from raw infrastructure to a mature, well-governed data platform."

*Why this works: Shows Paulo thinks about the full picture, not just individual tools. Opens a conversation about where he can add value.*

---

### Q2. Data Sources and Integration Complexity

"How many distinct data sources does the data team currently integrate, and what is the mix between internal systems, third-party APIs, and blockchain/on-chain data? What is the most challenging integration today?"

*Why this works: Demonstrates understanding that real data engineering difficulty is in source diversity and integration, not just running Spark jobs.*

---

### Q3. Team Structure and Collaboration

"How is the data team structured — is it centralized, embedded in product teams, or moving toward a Data Mesh model? How does the data engineering team interact with analytics, product, and compliance?"

*Why this works: Shows senior-level awareness that organizational structure impacts technical decisions. Paulo has experience across centralized (Natura) and distributed models.*

---

### Q4. Tech Debt and Modernization

"What does the current tech debt landscape look like for data infrastructure? Are there legacy systems or pipelines that the team is actively planning to modernize?"

*Why this works: Paulo has deep experience in modernization (Oracle to cloud at Cielo, stored procedures to PySpark at Itau, Impala to Redshift at Enel). This signals he is ready to tackle hard migration problems.*

---

### Q5. Data Quality and Governance Maturity

"How mature is the organization's data quality and governance framework today? Is there automated data quality testing in place, or is that an area the team is looking to build out?"

*Why this works: Data quality is Paulo's strength — he built frameworks at Banco do Brasil and Itau. This question identifies whether he can add immediate impact.*

---

### Q6. Compliance and Regulatory Requirements

"Given the regulated nature of the business, how involved is the data engineering team in compliance and regulatory reporting? Are there specific regulatory frameworks (FCA, MiCA, etc.) that shape how you design data pipelines?"

*Why this works: Shows Paulo understands that in FinTech, compliance is not an afterthought — it is a first-class design constraint. His experience with Brazilian Central Bank regulations is directly relevant.*

---

### Q7. Real-Time vs. Batch Processing

"What is the current balance between batch and real-time data processing? Are there use cases where the team is looking to move from batch to streaming, or vice versa?"

*Why this works: Demonstrates architectural thinking about trade-offs. Paulo can discuss his experience with both paradigms and help the team make informed decisions.*

---

### Q8. On-Call and Incident Response

"What does the on-call rotation look like for data infrastructure? When a pipeline fails at 2 AM, what is the escalation process and what tooling supports incident response?"

*Why this works: A practical, senior-level question that shows Paulo cares about operational reliability — not just building things, but keeping them running. His 99.9% uptime SLA experience at Banco do Brasil backs this up.*

---

### Q9. Growth and Impact

"What does success look like for this role in the first 90 days, and what would a high-performing data engineer be working on a year from now? I want to understand both the immediate priorities and the longer-term vision."

*Why this works: Shows Paulo is thinking about impact and career trajectory, not just completing tickets. It also helps him assess whether the role matches his ambitions.*

---

### Q10. What Keeps You Here?

"What is the most exciting data challenge the team is working on right now, and what made you personally choose to work here?"

*Why this works: A human question that builds rapport with the interviewer. It also reveals genuine insights about the company culture and the most impactful work. Senior candidates ask this because they are evaluating the company as much as the company is evaluating them.*

---

*Document prepared for Paulo Eduardo dos Santos — March 2026*
*Target: Data Engineer roles at crypto/FinTech companies (BCB Group, Zinnia, and similar)*
