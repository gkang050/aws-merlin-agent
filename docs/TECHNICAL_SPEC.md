# MERLIN Technical Specification

This document translates the product goals in `docs/PRD.md` and the AWS Agent Hackathon requirements into a buildable architecture for the MERLIN (Marketplace Earnings & Revenue Learning Intelligence Network) prototype. It is intended to guide implementation, integration, and demo preparation for the hackathon submission.

## 1. Objectives & Success Criteria
- **Primary objective:** Deliver an Amazon-native growth agent that unifies seller data, reasons over performance trends, predicts outcomes, and can execute safe optimizations (pricing, advertising, inventory) with human-in-the-loop control.
- **MVP success metrics:** ingest curated seller datasets, surface at least three actionable insights via conversational and dashboard channels, trigger one guarded autonomous action, and package evidence (logs/dashboards/demo) that satisfies Devpost submission requirements.
- **Constraints:** Use AWS native services eligible under hackathon rules (Bedrock, Nova, SageMaker, Agent Core, QuickSight), avoid storing sensitive seller PII, and ensure all dependencies are open-source or properly licensed.

## 2. Architectural Overview
The high-level architecture is detailed in `docs/ARCHITECTURE.md`:

```
Seller Data Sources ─► API Gateway & Lambda ─► S3 Data Lake ─► AWS Glue ─► SageMaker ─► Bedrock Agent Core ─► QuickSight / Chat UI / Voice UI
                                                                      ▲                             ▲               │
                                                                      └────────────── EventBridge & Parameter Store ┘
```

### Core Domains
1. **Data Foundation:** Collect sales, advertising, pricing, and inventory data from seller exports or mocked feeds.
2. **Reasoning & Insights:** Use Amazon Nova for multimodal understanding and Bedrock Agents for contextual QA.
3. **Predictive Optimization:** Train SageMaker models to forecast demand and campaign ROI; expose endpoints for real-time inference.
4. **Autonomous Execution:** Leverage Bedrock Agent Core workflows plus EventBridge to orchestrate safe changes via mocked APIs.
5. **Experience Layer:** Deliver insights through a QuickSight dashboard, a chat UI (Lex + Streamlit), and optional Nova Sonic voice interface.

## 3. Component Breakdown

### 3.1 Data Ingestion & Storage
- **Input Sources:** CSV/JSON exports representing seller sales, ad campaigns, pricing, inventory (hosted in an S3 “landing” bucket). For demo, synthetic data generated via Python scripts under `src/aws_merlin_agent/data_gen/`.
- **API Gateway + Lambda:** Optional REST entry point for live uploads. Lambda validates schemas, strips PII, and stages data into `s3://merlin-${env}-landing/`.
- **AWS Glue Jobs:** Transform landing data into parquet tables (sales_fact, ad_fact, pricing_dim, inventory_dim) stored in `s3://merlin-${env}-curated/`; maintain Glue Data Catalog for Athena/QuickSight.
- **Metadata Store:** DynamoDB table `merlin_runs` tracks ingestion batches, dataset versions, and provenance.

### 3.2 Processing & Analytics
- **Amazon SageMaker:**  
  - **Processing Jobs:** Feature engineering pipelines (sales velocity, ad efficiency, price elasticity).  
  - **Model Training:** XGBoost regression (demand forecast) and classification (campaign at-risk flag). Models saved in SageMaker Model Registry.
  - **Batch Transform:** Generates what-if simulation outputs consumed by the agent.
- **Amazon QuickSight:** Dashboards for KPI tracking (GMV trends, ACOS, inventory risk). Connected via Athena to curated datasets.

### 3.3 Reasoning Layer
- **Amazon Bedrock (Nova family):**  
  - *Nova Pro Understanding:* Summarizes listings, creatives, and charts.  
  - *Nova Canvas/Reel:* Produces creative assets for demo scenarios.  
  - *Nova Sonic:* Powers voice prompts (optional).
- **Bedrock Agent Core:**  
  - Orchestrates tool calls: `get_metrics` (Athena query), `run_forecast` (invoke SageMaker endpoint), `simulate_action` (Lambda what-if job), `execute_action` (EventBridge workflow).  
  - Maintains guardrails (confidence thresholds, change limits) defined in JSON policy stored in Parameter Store.

### 3.4 Action Execution
- **AWS Lambda (Action Runner):** Applies approved actions against mocked seller APIs (hosted as LocalStack endpoints during demo) and records results to DynamoDB `merlin_actions`.
- **EventBridge Scheduler:** Supports recurring optimization checks and triggers the agent workflow every 6 hours in production; for demo, EventBridge:Rule invoked manually.
- **Step Functions (optional enhancement):** For multi-step updates (e.g., price change + ad bid adjustment with rollbacks).

### 3.5 User Interfaces
- **Chat UI:** Streamlit application embedded in `src/aws_merlin_agent/ui/chat_app.py` integrates with Bedrock Agent Core via API Gateway; supports text queries and attaches visualization snippets.
- **Voice UI:** Amazon Lex bot connected to Bedrock for text answers and Nova Sonic for synthesized voice; minimal for MVP (two intents: “performance overview”, “recommended action”).
- **Reporting:** QuickSight dashboard shared via reader link; key widgets exported as PNGs for Devpost submission.

## 4. Data Flow Summary
1. Seller uploads datasets (manual script or API). Lambda validates and saves to S3 landing.
2. AWS Glue ETL normalizes data into curated S3 tables; metadata updates DynamoDB.
3. SageMaker processing job enriches features; training job registers models; inference endpoint hosted for agent queries.
4. EventBridge triggers Bedrock Agent Core workflow. The agent:  
   a. Queries metrics via Athena.  
   b. Calls SageMaker forecast endpoint to predict SKU demand.  
   c. Runs `simulate_action` Lambda to estimate impact.  
   d. If confidence ≥ policy threshold and human approval given, dispatches `execute_action` Lambda.
5. Actions and insights written to DynamoDB and surfaced in QuickSight and the chat UI. Nova Canvas/Reel outputs stored in `s3://merlin-${env}-creative/` and linked in the UI.

## 5. Environment & Deployment Plan
- **Environments:** `dev` (personal AWS account), `demo` (hackathon presentation). Each environment uses unique S3 buckets, IAM roles, and Parameter Store namespaces.
- **Infrastructure as Code:** AWS CDK (Python) module `infra/` provisions core services (S3, Glue, SageMaker endpoints, EventBridge rules, DynamoDB tables, IAM roles, API Gateway, Lambda, QuickSight data sources). Separate stack for UI hosting (Streamlit on ECS/Fargate or CloudFront + Amplify Hosting).
- **CI/CD Pipeline:** GitHub Actions (triggered on push) running linting (`ruff`, `black`), tests (`pytest`), and packaging; deployment jobs require manual approval (satisfies hackathon policies).

## 6. Security, Compliance & Observability
- **Identity & Access:** IAM roles with least privilege per component; cross-service access mediated via dedicated role assumption (e.g., Agent Core execution role limited to specific tools). Secrets stored in AWS Secrets Manager or Parameter Store (never in code).  
- **Data Handling:** Pseudonymize seller IDs during ingestion, encrypt S3 buckets with SSE-S3, enable CloudTrail audit logs, and apply S3 object-level access logging.  
- **Guardrails:** Agent policy enforced via Bedrock Guardrails JSON (rate limits, restricted actions). Change thresholds (price ±10%, bid <20%) configurable.  
- **Monitoring:** CloudWatch metrics/alarms for Lambda errors, SageMaker endpoint latency, EventBridge failures. QuickSight anomaly detection flags sudden KPI swings.  
- **Cost Controls:** Use spot training jobs, auto-stop SageMaker notebooks, and disable EventBridge schedules post-demo.

## 7. Testing Strategy
- **Unit Tests:** Python tests under `tests/` for data transformations, model-serving wrappers, and agent tool adapters.  
- **Integration Tests:** LocalStack-backed workflows to validate Lambda + DynamoDB + S3 interactions.  
- **Simulation Tests:** SageMaker processing scripts run on sample data to generate baseline forecasts; results validated against expected trends.  
- **End-to-End Demo Rehearsal:** Automated script (`scripts/demo_run.py`) seeds data, triggers the agent, and captures logs/screenshots for Devpost submission.

## 8. Demo & Submission Assets
- **Demo Runbook:**  
  1. Execute `scripts/bootstrap_env.sh` to deploy infrastructure.  
  2. Load synthetic datasets with `python -m scripts.load_sample_data --env demo`.  
  3. Start Streamlit UI (`streamlit run src/aws_merlin_agent/ui/chat_app.py`).  
  4. Trigger agent (`aws events invoke ...`).  
  5. Record agent chat, QuickSight dashboard, and Nova Canvas assets via OBS or Loom.
- **Submission Package:**  
  - Architecture diagram (see `docs/ARCHITECTURE.md` for complete diagrams).  
  - 2–3 minute video walkthrough.  
  - Repository link with README instructions.  
  - Documentation of AWS services used (aligned with hackathon Section 6).  
  - Security statement describing guardrails and data handling.

## 9. Open Questions & Next Steps
- Confirm availability of Amazon Nova services in the demo region; fallback to Bedrock Claude/SageMaker JumpStart if Nova access is limited.  
- Decide between Bedrock Agent Core built-in orchestration vs. custom LangChain agent hosted on SageMaker (must align with hackathon’s required technologies).  
- Clarify QuickSight licensing for demo (may use reader account or export static visuals).  
- Finalize dataset schema and ensure examples comply with hackathon IP rules.

Once these items are resolved, implementation can proceed following the architecture above. This specification will evolve with design reviews and AWS service availability updates.
