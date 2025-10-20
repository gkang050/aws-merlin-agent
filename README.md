# MERLIN AI Agent 🧙‍♂️

**M**arketplace **E**arnings & **R**evenue **L**earning **I**ntelligence **N**etwork

An autonomous AI agent for e-commerce marketplace sellers, built with Amazon Bedrock Agent Core, Nova Pro, and SageMaker AI.

---

**Quick Links:**
- [Quick Start](#quick-start) - Get running locally in 5 minutes
- [Testing](#testing) - Run tests
- [AWS Deployment](#aws-deployment) - Deploy to AWS
- [Architecture](docs/ARCHITECTURE.md) - System design
- [PRD](docs/PRD.md) - Product requirements

## Overview

MERLIN empowers e-commerce marketplace sellers through:

- **Conversational AI**: Natural language queries powered by Amazon Nova Pro and Bedrock Agent Core
- **ML Forecasting**: Demand predictions with SageMaker XGBoost (97.9% R² accuracy)
- **Performance Analysis**: LLM-powered insights on sales, advertising, and inventory
- **Multimodal AI**: Product image and video generation with Nova Canvas/Reel
- **Autonomous Execution**: Scheduled optimization runs with human oversight
- **Data Pipeline**: Unified analytics across S3, Glue, Athena, and DynamoDB

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- AWS account with Bedrock access (for full functionality)
- AWS CLI configured

### Local Development

Run MERLIN locally with mock data:

```bash
# 1. Install dependencies
pip install poetry
poetry install

# 2. Set environment variables
export AWS_REGION=us-east-1
export MERLIN_ENV=dev
export MERLIN_INFERENCE_MODE=local

# 3. Start the chat interface
poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py
```

The UI will open at `http://localhost:8501`. Try asking:
- "How is SKU-001 performing?"
- "Generate a demand forecast"
- "What should I optimize?"

### Testing

```bash
# Run all tests
poetry run pytest

# Run unit tests only (no AWS required)
poetry run pytest -m "not integration"

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing
```

### AWS Deployment

Deploy the complete infrastructure:

```bash
# 1. Configure AWS credentials
export CDK_DEFAULT_ACCOUNT=<your-aws-account-id>
export CDK_DEFAULT_REGION=us-east-1

# 2. Bootstrap CDK (first time only)
poetry run cdk bootstrap -c env=demo

# 3. Deploy infrastructure
poetry run cdk deploy -c env=demo --all

# 4. Load sample data
poetry run python scripts/load_sample_data.py --env demo

# 5. Train ML model
poetry run python -m aws_merlin_agent.models.training.pipeline --env demo

# 6. Deploy with SageMaker endpoint
poetry run cdk deploy -c env=demo \
  -c forecastModelArtifact=<s3-model-uri> --all
```

### Verify Bedrock Access

Ensure you have access to required models:

```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query 'modelSummaries[?contains(modelId, `nova`) || contains(modelId, `claude`)].modelId'
```

If models aren't accessible, request access in AWS Console → Bedrock → Model access.

## Project Structure

```
aws-merlin-agent/
├── src/aws_merlin_agent/     # Application source code
│   ├── agent/                # Agent workflows and tools
│   ├── models/               # ML training and inference
│   ├── data_ingestion/       # ETL and data pipelines
│   ├── features/             # Feature engineering
│   ├── ui/                   # Streamlit interface
│   └── config/               # Configuration management
├── infra/                    # AWS CDK infrastructure
│   ├── stacks/               # CDK stack definitions
│   └── cdk_app.py            # CDK app entry point
├── tests/                    # Test suites
├── scripts/                  # Utility scripts
├── docs/                     # Documentation
├── configs/                  # Environment configurations
└── data/                     # Sample data and schemas
```

## Deployment

### Local Development

```bash
# Set environment variables
export MERLIN_ENV=dev
export AWS_REGION=us-east-1
export MERLIN_INFERENCE_MODE=local

# Run Streamlit UI
poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py
```

### AWS Deployment

```bash
# Bootstrap CDK (first time only)
export CDK_DEFAULT_ACCOUNT=<your-aws-account-id>
export CDK_DEFAULT_REGION=us-east-1
poetry run cdk bootstrap -c env=demo

# Deploy infrastructure
poetry run cdk deploy -c env=demo --all
```

See [`docs/demo-guide.md`](docs/demo-guide.md) for detailed deployment instructions.

## Features

### 1. Demand Forecasting
- XGBoost-based ML model with 97.9% R² accuracy
- Feature engineering with lag variables and trends
- Real-time and batch inference
- Works across multiple marketplace platforms

### 2. Data Pipeline
- S3-based data lake (landing → curated)
- AWS Glue for ETL transformations
- DynamoDB for model registry
- Athena for ad-hoc queries
- Supports multiple data sources (CSV, JSON, API)

### 3. Agent Capabilities
- Natural language interface (Streamlit chat)
- Bedrock-powered analysis and recommendations
- Multi-platform support (Amazon, eBay, Shopify, etc.)
- Guardrails for safe execution
- Audit logs for all actions

### 4. Infrastructure
- Serverless architecture (Lambda, S3, DynamoDB)
- Infrastructure as Code (AWS CDK)
- Auto-scaling and cost-optimized
- Multi-environment support (dev, demo, prod)

## Development

### Code Quality

```bash
# Lint code
poetry run ruff check src tests

# Format code
poetry run black src tests

# Run tests with coverage
poetry run pytest --cov=src --cov-report=term-missing
```

### Adding Features

1. Create feature branch
2. Implement changes in `src/aws_merlin_agent/`
3. Add tests in `tests/`
4. Update documentation in `docs/`
5. Run linting and tests
6. Submit pull request

## Architecture

MERLIN uses a serverless, event-driven architecture:

- **AI Layer**: Bedrock Agent Core, Nova Pro (reasoning), Nova Canvas/Reel (multimodal), SageMaker (ML)
- **Data Layer**: S3 (data lake), DynamoDB (metadata), Athena (queries), Glue (ETL)
- **Compute Layer**: Lambda (orchestration), EventBridge (scheduling)
- **Interface Layer**: Streamlit (chat UI), API Gateway (optional)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture diagrams and design decisions.

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design
- **[PRD.md](docs/PRD.md)** - Product vision and requirements
- **[TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md)** - Detailed technical specification
- **[AGENTS.md](AGENTS.md)** - Development guidelines and conventions

## Testing

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/models/test_training_pipeline.py

# Run with coverage
poetry run pytest --cov=src --cov-report=html
```

## Supported Marketplaces

MERLIN is designed to work with any e-commerce marketplace:

- **Amazon** - Seller Central, Advertising Console
- **eBay** - Seller Hub, Promoted Listings
- **Shopify** - Store analytics, marketing data
- **Etsy** - Shop stats, advertising
- **Walmart** - Seller Center
- **Custom** - Any marketplace with CSV/JSON export

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for classes and public methods
4. Maintain >90% test coverage
5. Update documentation for new features

## License

Copyright © 2025 MERLIN Team

## Contact

For questions or support, please open an issue in the repository.

---

Built with ❤️ using AWS GenAI Stack
