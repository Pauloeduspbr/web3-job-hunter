# Paulo Eduardo dos Santos

**Engenheiro de Dados Sênior | Especialista em Cloud & Big Data | FinTech & Ativos Digitais**

Americana — São Paulo, Brasil (Aberto a Remoto) | +55 11 91526-7337 | paulo_eduardosp@yahoo.com.br
LinkedIn: linkedin.com/in/paulo--eduardo | GitHub: github.com/Pauloeduspbr

---

## RESUMO PROFISSIONAL

Engenheiro de Dados Sênior com 9 anos de experiência projetando e operando plataformas de dados de larga escala para bancos, meios de pagamento, telecom, saúde e e-commerce que processam milhões de transações diárias. Especialista em arquitetura de Data Lake / Lakehouse e Data Warehouse (Medallion Bronze/Silver/Gold, Star/Snowflake), design de pipelines ETL/ELT, governança e qualidade de dados, e migrações multi-cloud em AWS, Azure e GCP.

Mão na massa em todo o stack moderno de dados — Python, SQL, PySpark/Spark, Airflow, dbt, Kafka, Snowflake e Iceberg/Delta Lake — com resultados comprovados: 99,9% de SLA de disponibilidade, 60% de redução de armazenamento, 50% mais rápido em processamento e 70% menos operação manual. Autor de projetos open-source públicos de dados blockchain (Ethereum, Solana, DeFi), unindo engenharia de dados corporativa a Web3/FinTech.

---

## SKILLS TÉCNICAS

**Linguagens:** Python (avançado), SQL (avançado), PySpark, Shell Script, Scala

**Cloud:** AWS (S3, EMR / EMR Serverless, Glue, Athena, Redshift, Lambda, Kinesis, Lake Formation, DMS, Step Functions, KMS, CloudWatch) · Azure (Data Lake, Databricks, Data Factory, Synapse, Unity Catalog, Fabric) · GCP (BigQuery, Dataproc)

**Processamento & Orquestração:** Apache Spark, PySpark, SparkSQL, Apache Airflow, Apache NiFi, dbt, Kafka, Talend, DataStage, SSIS, Informatica PowerCenter/BDM, Sqoop, Flume

**Arquitetura:** Big Data (ecossistemas Hadoop/Spark), Data Lake & Lakehouse (Bronze/Silver/Gold), Data Warehouse (Star/Snowflake), Modelagem Dimensional, CDC, Event-Driven, Migração para Nuvem (on-prem → cloud)

**Lakehouse & Formatos:** Delta Lake, Apache Iceberg, Apache Hudi, Parquet

**Bancos de Dados:** Snowflake, SQL Server, Oracle, Teradata, PostgreSQL, MySQL, Redshift, MongoDB, Cassandra, HBase, DynamoDB

**Governança & Qualidade:** frameworks de Data Quality, Governança de Dados, Catálogo de Dados (AWS Glue, Unity Catalog), conformidade PII/LGPD, HashiCorp Vault, AWS KMS, criptografia Fernet

**DevOps & IaC:** Docker, Kubernetes, Terraform, Ansible, CI/CD, Git

**Visualização:** Power BI, QlikSense, Tableau, Spotfire, MicroStrategy, OBIEE, Grafana

**Metodologias:** Ágil para Analytics (Scrum, SAFe), levantamento de requisitos em projetos de analytics

---

## PRINCIPAIS RESULTADOS

- **99,9% de SLA de disponibilidade** no ambiente Big Data do Banco do Brasil, processando milhões de transações diárias
- Redução de **40%** no tempo de manutenção via framework reutilizável de automação em Python
- **60% de redução de armazenamento** migrando tabelas SQL legadas para Parquet/Delta Lake
- Redução de **50%** no tempo de processamento via otimização de clusters Big Data na Claro Brasil
- Redução de **70%** na intervenção manual via pipelines de Azure Automation
- Liderança em **migração multi-cloud** (Oracle → AWS + Azure + GCP) de dados de pagamento da Cielo
- Data Lake de saúde em Apache Iceberg com **governança PII/LGPD** completa (Vault, KMS, Fernet)

---

## EXPERIÊNCIA PROFISSIONAL

### Engenheiro de Dados — BRQ
**Jul 2025 – Atual | Remoto, Brasil**

**RD Saúde — Data Lake de Saúde (Visão 360 do Cliente)**
- Construção de Data Lake de saúde com arquitetura Medallion (Bronze/Silver/Gold) em Apache Iceberg sobre S3, suportando prontuário eletrônico, agendamento, vacinas, medicamentos, receituário e teleinterconsulta (Amplimed, HAOC, Vitat).
- Desenvolvimento de pipelines PySpark/SparkSQL para ingestão, transformação e consolidação de dados clínicos em larga escala, com suporte a Apache Iceberg e Apache Hudi.
- Orquestração de DAGs no Airflow integradas a Spark on Kubernetes, com geração automatizada de manifests YAML via builders Python.
- Modelagem da tabela analítica Visão 360 integrando múltiplas fontes (CRM, agendamentos, eventos, interesses) via Trino, Athena e Redshift.
- Framework próprio de Data Quality (validações cross-origin, light checks, DLS validations) e catálogo de dados versionado em YAML.
- Governança e segurança de dados sensíveis de saúde (PII/LGPD) com HashiCorp Vault, AWS KMS e criptografia Fernet, incluindo pipelines de decrypt na landing.
- Integração de ingestão via APIs (Amplimed, HAOC, Precifica) com clientes assíncronos em S3 e tratamento de schemas evolutivos (JSON/Parquet/Iceberg).
- Observabilidade end-to-end (handlers de log, métricas Spark, exceptions, comentários de tabelas Iceberg) integrada a AWS SNS e Step Functions; manutenção de containers Docker (dev/qa/prod).

**Itaú — Modernização e Analytics**
- Desenvolvimento de pipelines ETL com EMR Serverless e Glue Studio; otimização de consultas SQL e processos de data quality.
- Análise de testes A/B e desenvolvimento de análises de melhoria de métricas e validação de hipóteses.

---

### Especialista em Big Data / Engenheiro de Dados Sênior — Stefanini
**Jun 2023 – Jun 2025 | São Paulo, Brasil**

**Banco do Brasil — Sustentação de Ambiente Big Data**
- Sustentação e otimização de cluster Cloudera/Hortonworks em produção, garantindo **99,9% de SLA**.
- Automação em Python e Shell de processos operacionais; notebooks Jupyter para análise exploratória e jobs Ansible para gestão de infraestrutura.
- Otimização de consultas Hive e manutenção de estruturas HDFS; modelos dbt em Snowflake para relatórios financeiros com testes de qualidade e versionamento.

**AmericaNet — APIs e Processamento de Dados**
- API RESTful em Python Flask para exposição de dados processados; transformações complexas com SparkSQL no Databricks.
- Automação com Azure Automation e pipelines com tratamento de erros e logging; modelos ELT dbt/Snowflake com validações de integridade e Unity Catalog.

**Cielo — Dashboard Analytics**
- Análise e documentação de procedures Oracle legadas; scripts PySpark para grandes volumes e tabelas externas no Athena sobre S3 com particionamento.
- Migração de dados analíticos para Snowflake com modelagem dimensional dbt para dashboards em Power BI.

**Itaú — Refatoração de Processos ETL**
- Refatoração de tabelas SQL legadas para Parquet e conversão de stored procedures em jobs PySpark, alcançando **60% de redução de armazenamento**.
- Catálogo de dados com AWS Glue, processos de data quality e documentação técnica detalhada de todos os processos migrados.

**DirectLog — Sistema de Geolocalização**
- Esteira para captura de latitude/longitude via API Google Maps e DAGs Airflow para processamento batch de endereços.
- Interface web com acesso autenticado SFTP, hospedagem em EC2 e camada de cache para otimizar chamadas à API.

**Brasildev — Data Lake AWS**
- Data Lake em camadas (Bronze/Silver/Gold) com catálogo de dados e governança; motor de ingestão em Python com integração ao Salesforce.
- Políticas de segurança/acesso com Lake Formation e automação de infraestrutura com Terraform.

---

### Engenheiro de Dados Sênior — Natura & Co
**Fev 2022 – Jun 2023 | São Paulo, Brasil**

**Pipeline de E-commerce**
- Modelagem dimensional para analytics de e-commerce; pipelines ETL com EMR Serverless e DAGs Airflow para orquestração.
- Estruturas Delta Lake para versionamento e processos de carga incremental; integração com BI via Redshift.
- Modelos dbt em Snowflake para análise de comportamento de clientes com testes de qualidade.

**Cielo — Migração para Cloud e Modernização**
- Análise de estruturas Oracle e mapeamento para BigQuery; migração de dados legados para Azure Blob Storage e pipelines no Azure Data Factory com catálogo Unity Catalog.
- Conversão de lógicas SQL complexas para processamento distribuído; desenvolvimento de PySpark e SparkSQL no Databricks.

**JBS — Modernização de Pipeline de Dados**
- Liderança técnica de equipe de engenheiros e desenvolvedores.
- Cluster NiFi de alta disponibilidade integrado ao Active Directory; Application Load Balancer e fluxos NiFi para ingestão do SAP e movimentação S3↔Redshift.

---

### Engenheiro de Dados — Enel
**Mai 2021 – Fev 2022 | Brasil**

**Migração de Data Warehouse**
- Pipeline de migração com Talend Open Studio movendo dados do Impala para Redshift.
- Dashboards QlikSense conectados ao Redshift, documentação dos processos ETL, otimização de queries e treinamento das equipes de negócio.

---

### Arquiteto de Soluções Big Data — Banco do Nordeste
**Jan 2021 – Mai 2021 | Brasil**

**Data Lake Corporativo**
- Arquitetura de Data Lake com zonas raw, stage e analytics; cluster Hadoop não gerenciado e Dremio para a camada de analytics.
- Estrutura NoSQL com Cassandra para sistema de créditos; integração com sistemas legados via DataStage.

**Bradesco — Framework de Ingestão de Dados**
- Atualização dos scripts do framework de ingestão para tabelas Hive e HBase; automação em shell e integração ao scheduler IBM IWS; conexão com Teradata para extração.

---

### Arquiteto/Engenheiro Big Data — Hospital Sírio-Libanês
**Mar 2019 – Dez 2020 | São Paulo, Brasil**

**Plataforma de Analytics Hospitalar**
- Análise e ingestão de dados hospitalares de múltiplas fontes; instalação e configuração do Airflow para orquestração e DAGs ETL.
- Containers Docker integrados ao Airflow, Kubernetes para escalabilidade, integração AWS Cognito com Azure AD para SSO e pipeline CloudWatch→Elasticsearch via Lambda.

**Raízen — Framework de Ingestão de Dados**
- Levantamento da arquitetura de pipeline e análise de Azure Data Lake, Databricks e Power BI; documentação da integração SAP via SSIS Theobald.

**Dell EMC (Cliente: Fleury) — Consultoria & Treinamento**
- Sustentação de ambiente Hortonworks; segurança com Kerberos/Ranger e integração com AD; scripts de monitoração de jobs Oozie, dashboards Grafana e treinamento da equipe do cliente.

---

### Líder Técnico Big Data — Claro Brasil
**Set 2017 – Mar 2019 | São Paulo, Brasil**

**Implementação de Clusters Cloudera**
- Instalação e configuração de 3 clusters Cloudera (Data Lake, M2M, BI); Kerberos com AD como KDC e cross-realm entre clusters em domínios distintos.
- Integração Hive/Impala com ferramentas de BI (SAS, QlikView, Alteryx), framework de ingestão e scripts de monitoração, e Informatica BDM para ETL — reduzindo o tempo de processamento em **50%**. Mentoria e liderança de 2 engenheiros.

**Nextel — Sustentação e ETL**
- Processos ETL de ingestão, análise com Beeline/Impala, extração via Sqoop, levantamento de requisitos e sustentação do ambiente de produção.

---

### Analista Big Data — Vivo
**Jun 2017 – Set 2017 | Brasil**

**Migração e Sustentação Hadoop**
- Processos ETL de ingestão, análise com Hive e Python, migração de Hadoop 2.2 → 2.6, persistência em HBase e gestão do cluster com Zookeeper.

---

## FORMAÇÃO ACADÊMICA

- **Tecnólogo em Big Data e Inteligência de Dados** — Universidade Anhembi Morumbi | Previsto 2026
- **Inteligência Artificial** (em andamento) — FMU
- **Bacharelado em Sistemas de Informação** — UNIP | 2006

---

## CERTIFICAÇÕES

- Big Data Engineering — Garre Training (160h) | 2014
- Oracle Business Intelligence Suite — Garre Training (80h) | 2011
- Red Hat Certified System Administrator (RHCSA) — RedHat | 2008
- Cisco Certified Network Associate (CCNA) — IBTA | 2007
- Microsoft Certified Systems Engineer — Impacta | 2004

---

## PROJETOS OPEN-SOURCE (github.com/Pauloeduspbr)

- **dune-analytics-queries** — 12 queries SQL no Dune analisando dados blockchain: métricas de protocolos DeFi, mercados NFT, atividade em Ethereum e Solana, comparações cross-chain.
- **crypto-data-pipeline** — pipeline ingerindo dados de mercado de 100 criptoativos (CoinGecko API) com Airflow, PostgreSQL e Docker; 7/7 verificações de qualidade aprovadas.
- **medallion-data-lake** — template production-ready Bronze/Silver/Gold com Airflow, dbt e Terraform (AWS + GCP), dimensões SCD Tipo 2 e 36 testes automatizados.

---

## IDIOMAS

- **Português:** Nativo
- **Inglês:** Intermediário superior (B2) — leitura e escrita técnica fluentes
