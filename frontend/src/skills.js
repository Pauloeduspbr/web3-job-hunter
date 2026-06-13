// Pretty labels for the snake_case skill keys produced by score_jobs.py.
// Source of truth for the canonical keys: src/score_jobs.py SKILL_LEXICON.
// We NEVER invent skills here — only humanize keys the backend already emits.

const OVERRIDES = {
  sql: 'SQL',
  pyspark: 'PySpark',
  spark: 'Spark',
  aws: 'AWS',
  gcp: 'GCP',
  s3: 'S3',
  emr: 'EMR',
  emr_serverless: 'EMR Serverless',
  dbt: 'dbt',
  ci_cd: 'CI/CD',
  etl: 'ETL',
  cdc: 'CDC',
  bigquery: 'BigQuery',
  postgresql: 'PostgreSQL',
  mysql: 'MySQL',
  sql_server: 'SQL Server',
  mongodb: 'MongoDB',
  dynamodb: 'DynamoDB',
  power_bi: 'Power BI',
  lgpd_pii: 'LGPD / PII',
  api_integration: 'API Integration',
  data_warehouse: 'Data Warehouse',
  data_lake: 'Data Lake',
  delta_lake: 'Delta Lake',
  dimensional_modeling: 'Dimensional Modeling',
  data_quality: 'Data Quality',
  data_governance: 'Data Governance',
  data_factory: 'Data Factory',
  machine_learning: 'Machine Learning',
  event_driven: 'Event-Driven',
  step_functions: 'Step Functions',
  lake_formation: 'Lake Formation',
  blockchain_data: 'Blockchain Data',
  kubernetes: 'Kubernetes',
  nifi: 'NiFi',
  kafka: 'Kafka',
  airflow: 'Airflow',
  databricks: 'Databricks',
  snowflake: 'Snowflake',
  redshift: 'Redshift',
  athena: 'Athena',
  glue: 'Glue',
  terraform: 'Terraform',
  docker: 'Docker',
  git: 'Git',
  hadoop: 'Hadoop',
  trino: 'Trino',
  iceberg: 'Iceberg',
  hudi: 'Hudi',
  parquet: 'Parquet',
  medallion: 'Medallion',
  data_mesh: 'Data Mesh',
  data_vault: 'Data Vault',
  azure: 'Azure',
  synapse: 'Synapse',
  fabric: 'Microsoft Fabric',
  dataproc: 'Dataproc',
  dataflow: 'Dataflow',
}

export function prettySkill(key) {
  if (!key) return ''
  if (OVERRIDES[key]) return OVERRIDES[key]
  return String(key)
    .split('_')
    .map((w) => (w.length <= 3 ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)))
    .join(' ')
}

// Tier helpers shared across components — single source of truth for color/labels.
export function scoreTier(score) {
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

export const TIER_LABEL = {
  high: 'Forte match',
  mid: 'Match parcial',
  low: 'Match baixo',
}

export const TIER_COLOR = {
  high: 'var(--ok)',
  mid: 'var(--warn)',
  low: 'var(--danger)',
}
