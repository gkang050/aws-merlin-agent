# MERLIN Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MERLIN AI Agent System                              │
│              Marketplace Earnings & Revenue Learning Intelligence Network        │
│                     Multi-Platform E-Commerce Intelligence                       │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │  Streamlit UI    │    │   API Gateway    │    │  EventBridge     │          │
│  │  (Chat Interface)│    │   (REST API)     │    │  (Scheduled)     │          │
│  │                  │    │                  │    │                  │          │
│  │  • Chat messages │    │  • Data upload   │    │  • Every 6 hours │          │
│  │  • Reasoning     │    │  • Webhooks      │    │  • Autonomous    │          │
│  │    traces        │    │                  │    │    execution     │          │
│  │  • Quick actions │    │                  │    │                  │          │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘          │
│           │                       │                       │                     │
└───────────┼───────────────────────┼───────────────────────┼─────────────────────┘
            │                       │                       │
            └───────────────────────┴───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AI AGENT ORCHESTRATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Bedrock Agent Core Orchestrator                       │   │
│  │                   (BedrockAgentOrchestrator)                             │   │
│  │                                                                           │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │              Amazon Nova Pro (Reasoning LLM)                      │   │   │
│  │  │              Model: amazon.nova-pro-v1:0                          │   │   │
│  │  │                                                                    │   │   │
│  │  │  • Natural language understanding                                 │   │   │
│  │  │  • Multi-step reasoning                                           │   │   │
│  │  │  • Decision making                                                │   │   │
│  │  │  • Recommendation generation                                      │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                           │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │         Claude 3 Sonnet (Fallback LLM)                            │   │   │
│  │  │         Model: anthropic.claude-3-sonnet-20240229-v1:0            │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                           │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Action Groups                                  │   │   │
│  │  │                                                                    │   │   │
│  │  │  1. MetricsAnalysis                                               │   │   │
│  │  │     • Query seller performance data                               │   │   │
│  │  │     • Analyze trends                                              │   │   │
│  │  │                                                                    │   │   │
│  │  │  2. DemandForecasting                                             │   │   │
│  │  │     • Generate ML predictions                                     │   │   │
│  │  │     • What-if simulations                                         │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                   │
└───────────────────────────────────────┬───────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TOOL INTEGRATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐              │
│  │  Metrics Query   │  │  ML Forecasting  │  │  Creative Gen    │              │
│  │  Tool            │  │  Tool            │  │  Tool            │              │
│  │                  │  │                  │  │                  │              │
│  │  • Athena SQL    │  │  • SageMaker     │  │  • Nova Canvas   │              │
│  │  • Data fetch    │  │    endpoint      │  │  • Nova Reel     │              │
│  │  • Aggregation   │  │  • XGBoost model │  │  • Image gen     │              │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘              │
│           │                     │                     │                         │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA & COMPUTE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         Data Platform                                    │   │
│  │                                                                           │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │   │
│  │  │  S3 Landing  │───▶│  AWS Glue    │───▶│  S3 Curated  │              │   │
│  │  │  Bucket      │    │  ETL Jobs    │    │  Bucket      │              │   │
│  │  │              │    │              │    │              │              │   │
│  │  │  • Raw CSV   │    │  • Transform │    │  • Parquet   │              │   │
│  │  │  • JSON data │    │  • Validate  │    │  • Optimized │              │   │
│  │  └──────────────┘    └──────────────┘    └──────┬───────┘              │   │
│  │                                                   │                       │   │
│  │                                                   ▼                       │   │
│  │                                          ┌──────────────┐                │   │
│  │                                          │  Athena      │                │   │
│  │                                          │  Query Eng   │                │   │
│  │                                          │              │                │   │
│  │                                          │  • SQL       │                │   │
│  │                                          │  • Analytics │                │   │
│  │                                          └──────────────┘                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      Machine Learning Platform                           │   │
│  │                                                                           │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │   │
│  │  │  SageMaker   │───▶│  SageMaker   │───▶│  SageMaker   │              │   │
│  │  │  Processing  │    │  Training    │    │  Endpoint    │              │   │
│  │  │              │    │              │    │              │              │   │
│  │  │  • Feature   │    │  • XGBoost   │    │  • Real-time │              │   │
│  │  │    engineer  │    │  • 97.9% R²  │    │    inference │              │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      Multimodal AI Platform                              │   │
│  │                                                                           │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │   │
│  │  │  Nova Canvas │    │  Nova Reel   │    │  Nova Pro    │              │   │
│  │  │              │    │              │    │  Vision      │              │   │
│  │  │  • Image gen │    │  • Video gen │    │              │              │   │
│  │  │  • 1024x1024 │    │  • 6 sec max │    │  • Image     │              │   │
│  │  │              │    │              │    │    analysis  │              │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         Metadata & State                                 │   │
│  │                                                                           │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │   │
│  │  │  DynamoDB    │    │  DynamoDB    │    │  DynamoDB    │              │   │
│  │  │  Runs Table  │    │  Actions     │    │  Model       │              │   │
│  │  │              │    │  Table       │    │  Registry    │              │   │
│  │  │  • Run logs  │    │  • Action    │    │  • Versions  │              │   │
│  │  │  • Metadata  │    │    history   │    │  • Metrics   │              │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION & EXECUTION LAYER                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │  Lambda          │    │  EventBridge     │    │  Step Functions  │          │
│  │  Agent Runner    │    │  Scheduler       │    │  (Optional)      │          │
│  │                  │    │                  │    │                  │          │
│  │  • Workflow exec │◀───│  • Cron: 6h     │    │  • Multi-step    │          │
│  │  • Tool calls    │    │  • Triggers      │    │  • Rollback      │          │
│  │  • Error handle  │    │                  │    │                  │          │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘          │
│                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE & SECURITY LAYER                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │  IAM Roles       │    │  CloudWatch      │    │  AWS CDK         │          │
│  │                  │    │                  │    │                  │          │
│  │  • Least priv    │    │  • Logs          │    │  • IaC           │          │
│  │  • Service roles │    │  • Metrics       │    │  • Multi-env     │          │
│  │  • Policies      │    │  • Alarms        │    │  • Reproducible  │          │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘          │
│                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```


## Data Flow Diagrams

### 1. Conversational Query Flow

```
User Query
    │
    ▼
┌─────────────────────┐
│  Streamlit UI       │
│  chat_app.py        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MerlinAgentWorkflow│
│  agent_plan.py      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  BedrockAgentOrchestrator               │
│  bedrock_agent.py                       │
│                                         │
│  1. Parse user intent                   │
│  2. Select action group                 │
│  3. Invoke Nova Pro for reasoning       │
│  4. Execute tools as needed             │
│  5. Generate response                   │
└──────────┬──────────────────────────────┘
           │
           ├─────────────────┬─────────────────┬─────────────────┐
           ▼                 ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  Athena  │      │SageMaker │     │   Nova   │     │DynamoDB  │
    │  Query   │      │ Endpoint │     │  Canvas  │     │  Tables  │
    └──────────┘      └──────────┘     └──────────┘     └──────────┘
           │                 │                 │                 │
           └─────────────────┴─────────────────┴─────────────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │  Response    │
                            │  with trace  │
                            └──────────────┘
```

### 2. Autonomous Execution Flow

```
EventBridge Schedule (Every 6 hours)
    │
    ▼
┌─────────────────────┐
│  Lambda Trigger     │
│  agent_plan.py      │
│  lambda_handler()   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Fetch Recent Data  │
│  • Query Athena     │
│  • Get metrics      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Analyze with LLM   │
│  • Nova Pro         │
│  • Summarize trends │
│  • Identify issues  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Forecast  │
│  • SageMaker        │
│  • Predict demand   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Recommend Actions  │
│  • Price changes    │
│  • Ad adjustments   │
│  • Inventory alerts │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Log to DynamoDB    │
│  • Run metadata     │
│  • Actions taken    │
└─────────────────────┘
```

### 3. Data Ingestion & Processing Flow

```
Seller Data Sources
    │
    ▼
┌─────────────────────┐
│  API Gateway        │
│  (Optional)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Lambda Validator   │
│  • Schema check     │
│  • PII removal      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  S3 Landing Bucket  │
│  • Raw CSV/JSON     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AWS Glue ETL       │
│  • Transform        │
│  • Normalize        │
│  • Enrich           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  S3 Curated Bucket  │
│  • Parquet format   │
│  • Partitioned      │
└──────────┬──────────┘
           │
           ├─────────────────┬─────────────────┐
           ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐     ┌──────────┐
    │  Athena  │      │SageMaker │     │  Glue    │
    │  Queries │      │ Training │     │ Catalog  │
    └──────────┘      └──────────┘     └──────────┘
```


### 4. ML Training & Inference Flow

```
Curated Data (S3)
    │
    ▼
┌─────────────────────┐
│  SageMaker          │
│  Processing Job     │
│                     │
│  • Feature eng      │
│  • Lag variables    │
│  • Aggregations     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  SageMaker          │
│  Training Job       │
│                     │
│  • XGBoost          │
│  • Hyperparameter   │
│    tuning           │
│  • Cross-validation │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Model Registry     │
│  (DynamoDB)         │
│                     │
│  • Version: v1.2    │
│  • R²: 0.979        │
│  • S3 URI           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  SageMaker          │
│  Endpoint           │
│                     │
│  • ml.m5.xlarge     │
│  • Auto-scaling     │
└──────────┬──────────┘
           │
           ▼
    Agent Queries
```

## Component Details

### Marketplace Adapters

MERLIN uses a plugin architecture to support multiple e-commerce platforms:

#### Adapter Pattern
```python
class MarketplaceAdapter:
    def fetch_sales_data(self, date_range) -> DataFrame
    def fetch_ad_data(self, date_range) -> DataFrame
    def update_price(self, sku, new_price) -> bool
    def update_ad_bid(self, campaign_id, new_bid) -> bool
```

#### Supported Platforms
- **Amazon** - SP-API, Advertising API
- **eBay** - Trading API, Marketing API
- **Shopify** - Admin API, GraphQL
- **CSV/JSON** - Generic import for any platform

#### Data Normalization
All marketplace data is normalized to a common schema:
- `seller_id`, `marketplace`, `sku`, `sale_date`
- `units_sold`, `net_revenue`, `ad_spend`
- `inventory_on_hand`, `price`

### AI Agent Components

#### 1. BedrockAgentOrchestrator
**File:** `src/aws_merlin_agent/agent/bedrock_agent.py`

**Responsibilities:**
- Orchestrate agent workflows across all marketplaces
- Manage conversation sessions
- Route to appropriate action groups
- Handle reasoning traces
- Fallback management (Nova → Claude)

**Key Methods:**
- `invoke_agent()` - Main entry point
- `_invoke_inline_agent()` - Inline agent execution
- `_invoke_deployed_agent()` - Pre-deployed agent
- `_fallback_to_claude()` - Fallback logic

#### 2. Bedrock Summary Tool
**File:** `src/aws_merlin_agent/agent/tools/bedrock_summary.py`

**Responsibilities:**
- Analyze performance data with LLM
- Generate actionable insights
- Explain trends and anomalies

**Models Used:**
- Primary: Amazon Nova Pro
- Fallback: Claude 3 Sonnet

#### 3. Metrics Query Tool
**File:** `src/aws_merlin_agent/agent/tools/metrics_query.py`

**Responsibilities:**
- Execute SQL queries via Athena
- Fetch seller performance data
- Parse and format results

#### 4. Nova Creative Tools
**File:** `src/aws_merlin_agent/creative/nova_assets.py`

**Capabilities:**
- `generate_listing_image()` - Nova Canvas
- `generate_promotional_video()` - Nova Reel
- `analyze_product_image()` - Nova Pro Vision

### Data Platform Components

#### 1. S3 Data Lake
**Buckets:**
- `merlin-{env}-landing` - Raw data ingestion
- `merlin-{env}-curated` - Processed parquet files
- `merlin-{env}-creative` - Generated assets

#### 2. AWS Glue
**Jobs:**
- ETL transformations
- Data quality checks
- Schema evolution

**Catalog:**
- Database: `merlin_{env}`
- Tables: `sales_fact`, `ad_fact`, `pricing_dim`, `inventory_dim`

#### 3. Amazon Athena
**Usage:**
- Ad-hoc SQL queries
- Performance analysis
- Data exploration

#### 4. DynamoDB Tables
**Tables:**
- `merlin_runs` - Execution metadata
- `merlin_actions` - Action history
- `merlin_models` - Model registry

### ML Platform Components

#### 1. SageMaker Processing
**Purpose:** Feature engineering
**Instance:** ml.m5.xlarge
**Output:** Training-ready datasets

#### 2. SageMaker Training
**Algorithm:** XGBoost
**Metrics:** R² = 0.979
**Output:** Model artifacts in S3

#### 3. SageMaker Endpoints
**Name:** `merlin-{env}-demand-forecast`
**Instance:** ml.m5.xlarge
**Scaling:** Auto-scaling enabled


## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Security Layers                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Identity & Access Management (IAM)                           │
│     ┌──────────────────────────────────────────────────────┐   │
│     │  • Agent Execution Role                               │   │
│     │    - Bedrock: InvokeModel, InvokeAgent               │   │
│     │    - SageMaker: InvokeEndpoint                        │   │
│     │    - Athena: StartQueryExecution, GetQueryResults    │   │
│     │    - S3: GetObject, PutObject                         │   │
│     │    - DynamoDB: GetItem, PutItem, Query               │   │
│     │                                                        │   │
│     │  • Lambda Execution Role                              │   │
│     │    - CloudWatch Logs: CreateLogGroup, PutLogEvents   │   │
│     │    - EventBridge: PutEvents                           │   │
│     │                                                        │   │
│     │  • SageMaker Execution Role                           │   │
│     │    - S3: Read/Write model artifacts                   │   │
│     │    - CloudWatch: Metrics and logs                     │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                   │
│  2. Data Encryption                                              │
│     ┌──────────────────────────────────────────────────────┐   │
│     │  • S3: SSE-S3 encryption at rest                      │   │
│     │  • DynamoDB: Encryption at rest (default)             │   │
│     │  • Athena: Query results encrypted                    │   │
│     │  • TLS 1.2+ for data in transit                       │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                   │
│  3. Network Security                                             │
│     ┌──────────────────────────────────────────────────────┐   │
│     │  • VPC endpoints for AWS services (optional)          │   │
│     │  • Security groups for compute resources              │   │
│     │  • Private subnets for sensitive workloads            │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                   │
│  4. Audit & Compliance                                           │
│     ┌──────────────────────────────────────────────────────┐   │
│     │  • CloudTrail: API call logging                       │   │
│     │  • CloudWatch Logs: Application logs                  │   │
│     │  • DynamoDB: Action audit trail                       │   │
│     │  • S3 Access Logs: Data access tracking               │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                   │
│  5. Guardrails                                                   │
│     ┌──────────────────────────────────────────────────────┐   │
│     │  • Price change limits: ±10%                          │   │
│     │  • Bid adjustment limits: <20%                        │   │
│     │  • Human-in-the-loop approval for critical actions   │   │
│     │  • Rate limiting on API calls                         │   │
│     └──────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Environment Setup                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Development (dev)                                               │
│  ├─ Personal AWS account                                         │
│  ├─ Local inference mode                                         │
│  ├─ Minimal resources                                            │
│  └─ Fast iteration                                               │
│                                                                   │
│  Demo (demo)                                                     │
│  ├─ Hackathon presentation                                       │
│  ├─ Full infrastructure                                          │
│  ├─ Sample data loaded                                           │
│  └─ SageMaker endpoints deployed                                 │
│                                                                   │
│  Production (prod)                                               │
│  ├─ Production AWS account                                       │
│  ├─ Auto-scaling enabled                                         │
│  ├─ Multi-AZ deployment                                          │
│  └─ Enhanced monitoring                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

Infrastructure as Code (AWS CDK)
├─ infra/cdk_app.py              # CDK app entry point
├─ infra/stacks/
│  ├─ data_platform_stack.py     # S3, Glue, DynamoDB, Athena
│  └─ agent_stack.py              # Lambda, SageMaker, EventBridge
└─ configs/
   ├─ dev/                        # Dev environment config
   └─ demo/                       # Demo environment config
```

## Scalability & Performance

### Horizontal Scaling
```
┌─────────────────────────────────────────────────────────────────┐
│  Component              │  Scaling Strategy                      │
├─────────────────────────┼────────────────────────────────────────┤
│  Lambda Functions       │  Automatic (up to 1000 concurrent)     │
│  SageMaker Endpoints    │  Auto-scaling based on invocations     │
│  DynamoDB Tables        │  On-demand capacity mode               │
│  S3 Storage             │  Unlimited (automatic)                 │
│  Athena Queries         │  Automatic parallelization             │
│  Bedrock API            │  AWS-managed scaling                   │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Optimizations
```
1. Data Layer
   • Parquet format for efficient columnar storage
   • Partitioning by date for faster queries
   • Glue Data Catalog for metadata caching

2. Compute Layer
   • Lambda warm starts with provisioned concurrency
   • SageMaker endpoint caching
   • Athena query result caching

3. AI Layer
   • Bedrock model response caching (session-based)
   • Batch inference for bulk predictions
   • Async processing for non-critical tasks
```


## Cost Optimization

```
┌─────────────────────────────────────────────────────────────────┐
│  Service              │  Cost Optimization Strategy              │
├─────────────────────────┼────────────────────────────────────────┤
│  Bedrock              │  • Use Nova Pro (cost-effective)         │
│                       │  • Cache responses when possible         │
│                       │  • Batch requests                        │
├─────────────────────────┼────────────────────────────────────────┤
│  SageMaker            │  • Use Spot instances for training       │
│                       │  • Auto-stop idle endpoints              │
│                       │  • Right-size instance types             │
├─────────────────────────┼────────────────────────────────────────┤
│  S3                   │  • Lifecycle policies (archive old data) │
│                       │  • Intelligent-Tiering storage class     │
│                       │  • Compress data (Parquet)               │
├─────────────────────────┼────────────────────────────────────────┤
│  Lambda               │  • Optimize memory allocation            │
│                       │  • Reduce cold starts                    │
│                       │  • Use ARM64 (Graviton2)                 │
├─────────────────────────┼────────────────────────────────────────┤
│  DynamoDB             │  • On-demand for variable workloads      │
│                       │  • TTL for temporary data                │
│                       │  • Efficient key design                  │
├─────────────────────────┼────────────────────────────────────────┤
│  Athena               │  • Partition pruning                     │
│                       │  • Columnar format (Parquet)             │
│                       │  • Query result caching                  │
└─────────────────────────────────────────────────────────────────┘

Estimated Monthly Cost (Demo Environment):
├─ Bedrock (Nova Pro): ~$50-100 (based on usage)
├─ SageMaker Endpoint: ~$200 (ml.m5.xlarge, 24/7)
├─ Lambda: ~$10 (within free tier)
├─ S3: ~$5 (100GB storage)
├─ DynamoDB: ~$5 (on-demand, low traffic)
├─ Athena: ~$5 (query costs)
├─ Glue: ~$10 (ETL jobs)
└─ Total: ~$285-335/month
```

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────────┐
│                      Monitoring Stack                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CloudWatch Metrics                                              │
│  ├─ Lambda: Invocations, Duration, Errors                        │
│  ├─ SageMaker: ModelLatency, Invocations                         │
│  ├─ Bedrock: TokenCount, Latency                                 │
│  ├─ DynamoDB: ConsumedReadCapacity, ThrottledRequests            │
│  └─ Custom: AgentSuccessRate, ForecastAccuracy                   │
│                                                                   │
│  CloudWatch Logs                                                 │
│  ├─ /aws/lambda/merlin-agent-orchestrator                        │
│  ├─ /aws/sagemaker/Endpoints/merlin-demand-forecast              │
│  └─ /aws/glue/jobs/merlin-etl                                    │
│                                                                   │
│  CloudWatch Alarms                                               │
│  ├─ Lambda errors > 5% → SNS notification                        │
│  ├─ SageMaker latency > 1s → Auto-scaling trigger                │
│  ├─ DynamoDB throttling → Capacity adjustment                    │
│  └─ Cost anomaly detection → Budget alert                        │
│                                                                   │
│  X-Ray Tracing (Optional)                                        │
│  ├─ End-to-end request tracing                                   │
│  ├─ Service map visualization                                    │
│  └─ Performance bottleneck identification                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer                │  Technologies                            │
├─────────────────────────┼────────────────────────────────────────┤
│  AI/ML                │  • Amazon Bedrock (Nova Pro, Claude)     │
│                       │  • Amazon Nova Canvas (images)           │
│                       │  • Amazon Nova Reel (videos)             │
│                       │  • Amazon SageMaker (XGBoost)            │
├─────────────────────────┼────────────────────────────────────────┤
│  Data Platform        │  • Amazon S3 (data lake)                 │
│                       │  • AWS Glue (ETL)                        │
│                       │  • Amazon Athena (queries)               │
│                       │  • Amazon DynamoDB (metadata)            │
├─────────────────────────┼────────────────────────────────────────┤
│  Compute              │  • AWS Lambda (serverless)               │
│                       │  • Amazon EventBridge (scheduling)       │
│                       │  • AWS Step Functions (optional)         │
├─────────────────────────┼────────────────────────────────────────┤
│  Frontend             │  • Streamlit (Python web app)            │
│                       │  • AWS App Runner (hosting)              │
├─────────────────────────┼────────────────────────────────────────┤
│  Infrastructure       │  • AWS CDK (Python)                      │
│                       │  • CloudFormation (generated)            │
├─────────────────────────┼────────────────────────────────────────┤
│  Programming          │  • Python 3.11                           │
│                       │  • Poetry (dependency management)        │
│                       │  • Pytest (testing)                      │
├─────────────────────────┼────────────────────────────────────────┤
│  Monitoring           │  • CloudWatch (logs, metrics, alarms)    │
│                       │  • CloudTrail (audit)                    │
│                       │  • X-Ray (tracing, optional)             │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Serverless-First Architecture
**Rationale:** Minimize operational overhead, auto-scaling, pay-per-use
**Trade-offs:** Cold starts, execution time limits

### 2. Bedrock Agent Core for Orchestration
**Rationale:** Native AWS integration, managed service, reasoning capabilities
**Trade-offs:** Vendor lock-in, less customization than DIY

### 3. Hybrid Intelligence (LLM + ML)
**Rationale:** Combine reasoning (LLM) with predictive accuracy (ML)
**Trade-offs:** Increased complexity, multiple model management

### 4. S3 Data Lake Pattern
**Rationale:** Scalable, cost-effective, supports multiple analytics tools
**Trade-offs:** Eventual consistency, query latency

### 5. Infrastructure as Code (CDK)
**Rationale:** Reproducible, version-controlled, multi-environment
**Trade-offs:** Learning curve, abstraction overhead

## Future Enhancements

```
Phase 2 (Post-Hackathon)
├─ Real-time streaming with Kinesis
├─ QuickSight dashboards for visualization
├─ Multi-seller support with tenant isolation
├─ Advanced guardrails with Bedrock Guardrails API
├─ A/B testing framework for recommendations
└─ Mobile app with voice interface (Nova Sonic)

Phase 3 (Production Scale)
├─ Multi-region deployment
├─ Advanced caching layer (ElastiCache)
├─ GraphQL API with AppSync
├─ Fine-tuned models for specific seller segments
├─ Integration with Amazon Seller Central API
└─ Marketplace for third-party plugins
```

---

**Document Version:** 1.0  
**Last Updated:** October 19, 2025  
**Maintained By:** MERLIN Team 🧙‍♂️
