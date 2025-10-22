# MERLIN Deployment Guide

## Free Demo Deployment (Recommended)

### Option 1: Streamlit Community Cloud (100% Free)

**Best for**: Quick public demo without AWS costs

#### Steps:

1. **Prepare Repository**
```bash
# Ensure code is pushed to GitHub
git add .
git commit -m "feat: ready for deployment"
git push origin main
```

2. **Deploy to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Repository: `your-username/aws-merlin-agent`
   - Branch: `main`
   - Main file path: `src/aws_merlin_agent/ui/chat_app.py`
   - Click "Deploy"

3. **Configure Environment Variables**

In Streamlit Cloud settings, add:
```
MERLIN_ENV=demo
MERLIN_INFERENCE_MODE=local
AWS_REGION=us-east-1
```

4. **Access Your Demo**
   - URL: `https://your-app-name.streamlit.app`
   - Share this URL publicly!

#### What Works in Free Mode:
- ✅ Full UI and chat interface
- ✅ Sample data visualization
- ✅ Architecture demonstration
- ✅ Mock forecasting (local mode)
- ❌ Real Bedrock API calls (requires AWS credentials)
- ❌ Real SageMaker inference

#### Limitations:
- No real AI responses (shows mock data)
- No AWS integration
- Perfect for UI/UX demo

---

## Full AWS Deployment (Paid)

### Prerequisites:
- AWS Account
- Bedrock model access (request in AWS Console)
- AWS CLI configured
- ~$50-100/month budget

### Steps:

1. **Request Bedrock Access**
```bash
# In AWS Console:
# 1. Go to Amazon Bedrock
# 2. Click "Model access"
# 3. Request access to:
#    - Amazon Nova Pro
#    - Claude 3 Sonnet
```

2. **Configure AWS**
```bash
export AWS_REGION=us-east-1
export CDK_DEFAULT_ACCOUNT=<your-account-id>
export CDK_DEFAULT_REGION=us-east-1
```

3. **Deploy Infrastructure**
```bash
# Bootstrap CDK (first time only)
poetry run cdk bootstrap -c env=demo

# Deploy all stacks
poetry run cdk deploy -c env=demo --all
```

4. **Load Sample Data**
```bash
poetry run python scripts/load_sample_data.py --env demo
```

5. **Train ML Model**
```bash
poetry run python -m aws_merlin_agent.models.training.pipeline --env demo
```

6. **Deploy with SageMaker Endpoint**
```bash
# Get model artifact URI from previous step
poetry run cdk deploy -c env=demo \
  -c forecastModelArtifact=s3://bucket/path/model.json \
  --all
```

7. **Deploy UI (Optional)**
```bash
# Deploy Streamlit on AWS App Runner
poetry run cdk deploy -c env=demo -c deployUI=true --all
```

### Estimated Costs:
- Bedrock (Nova Pro): ~$10-20/month (light usage)
- SageMaker Endpoint: ~$50/month (ml.m5.xlarge 24/7)
- Lambda: ~$5/month
- S3 + DynamoDB: ~$5/month
- **Total**: ~$70-80/month

### Cost Optimization:
- Stop SageMaker endpoint when not in use
- Use Spot instances for training
- Set up auto-shutdown for demo periods

---

## Hybrid Approach (Best for Demos)

### Free Public UI + Video Demo

1. **Deploy UI to Streamlit Cloud** (free)
   - Shows architecture and interface
   - Works with mock data

2. **Record Video Demo** (free)
   - Run locally with real AWS
   - Show full Bedrock integration
   - Upload to YouTube/Loom
   - Embed in README

3. **Add Screenshots** (free)
   - Capture key features
   - Add to `docs/screenshots/`
   - Include in documentation

### Example README Section:
```markdown
## Live Demo

- **UI Demo**: https://merlin-demo.streamlit.app (mock data)
- **Video Demo**: https://youtube.com/watch?v=... (full features)
- **Screenshots**: See [docs/screenshots/](docs/screenshots/)
```

---

## Alternative Free Platforms

### Hugging Face Spaces
```bash
# 1. Create space at https://huggingface.co/spaces
# 2. Select "Streamlit" as SDK
# 3. Upload code
# 4. Set environment variables
# 5. Get URL: https://huggingface.co/spaces/username/merlin
```

**Pros**: Free GPU, good for ML  
**Cons**: Slower than Streamlit Cloud

### Railway.app
```bash
# 1. Connect GitHub repo
# 2. Auto-deploys on push
# 3. $5 free credit/month
```

**Pros**: More control, background jobs  
**Cons**: Limited free tier

### Render.com
```bash
# 1. Connect GitHub
# 2. Select "Web Service"
# 3. Build: pip install -r requirements.txt
# 4. Start: streamlit run src/aws_merlin_agent/ui/chat_app.py
```

**Pros**: Easy setup, auto-deploys  
**Cons**: Spins down after inactivity

---

## Local Development

### Run Locally (Free)
```bash
# 1. Install dependencies
poetry install

# 2. Set environment
export MERLIN_ENV=dev
export MERLIN_INFERENCE_MODE=local
export AWS_REGION=us-east-1

# 3. Run Streamlit
poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py

# 4. Open browser
# http://localhost:8501
```

### With Real AWS (Requires Credentials)
```bash
# 1. Configure AWS CLI
aws configure

# 2. Set environment
export MERLIN_INFERENCE_MODE=sagemaker

# 3. Run Streamlit
poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py
```

---

## Troubleshooting

### Streamlit Cloud Issues

**App won't start:**
- Check `requirements.txt` includes all dependencies
- Verify Python version (3.11+)
- Check logs in Streamlit Cloud dashboard

**Import errors:**
- Ensure `src/` is in Python path
- Add to `streamlit.Dockerfile` if needed

**Memory issues:**
- Streamlit Cloud has 1GB RAM limit
- Reduce model size or use mock mode

### AWS Deployment Issues

**Bedrock access denied:**
- Request model access in AWS Console
- Wait 5-10 minutes for approval
- Check IAM permissions

**CDK deployment fails:**
- Verify AWS credentials
- Check account limits
- Review CloudFormation errors

**High costs:**
- Stop SageMaker endpoints when not in use
- Use on-demand instead of 24/7
- Monitor with AWS Cost Explorer

---

## Recommended Demo Setup

### For Hackathon/Portfolio:

1. ✅ **Streamlit Cloud** - Free public demo
2. ✅ **Video Recording** - Show full features locally
3. ✅ **Screenshots** - Document key features
4. ✅ **README badges** - Link to live demo

### For Production:

1. ✅ **AWS Full Deployment** - All features
2. ✅ **Auto-scaling** - Cost optimization
3. ✅ **Monitoring** - CloudWatch alerts
4. ✅ **CI/CD** - GitHub Actions

---

## Next Steps

1. Choose deployment option
2. Follow steps above
3. Test thoroughly
4. Share demo URL
5. Monitor costs (if using AWS)

For questions, open an issue in the repository.
