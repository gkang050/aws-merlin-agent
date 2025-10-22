# MERLIN Demo Video Guide

## 🎬 3-5 Minute Demo Script

### Setup (Before Recording)

```bash
# 1. Start Streamlit locally
export MERLIN_ENV=demo
export AWS_REGION=us-east-1
poetry run streamlit run src/aws_merlin_agent/ui/chat_app.py

# 2. Open browser to http://localhost:8501
# 3. Start screen recording (OBS, Loom, or QuickTime)
```

---

## 📝 Script (3-5 minutes)

### Intro (30 seconds)

**Say:**
> "Hi, I'm presenting MERLIN - a marketplace-agnostic AI agent for e-commerce sellers. MERLIN uses Amazon Bedrock Agent Core, Nova Pro, and SageMaker to help sellers across Amazon, eBay, Shopify, and other platforms optimize their business."

**Show:**
- Streamlit UI homepage
- Sidebar showing AWS services

---

### Demo 1: Conversational AI (60 seconds)

**Do:** Type in chat: "How is SKU-001 performing over the last 7 days?"

**Say:**
> "MERLIN uses Amazon Nova Pro for intelligent reasoning. Watch as it analyzes the data..."

**Show:**
- Agent response with insights
- Click "Agent Reasoning Trace" to show thinking process
- Point out: "Notice it analyzed 7 days of data, calculated ACOS, and provided recommendations"

---

### Demo 2: Multi-Platform Support (45 seconds)

**Say:**
> "Unlike competitors that only work with Amazon, MERLIN supports multiple marketplaces. It normalizes data from Amazon, eBay, Shopify, Etsy, and Walmart into a unified format."

**Show:**
- Open `docs/PRD.md` and scroll to "Supported Marketplaces"
- Show architecture diagram in `docs/ARCHITECTURE.md`
- Highlight marketplace adapter section

---

### Demo 3: ML Forecasting (45 seconds)

**Do:** Type: "Generate a demand forecast for the next week"

**Say:**
> "MERLIN combines LLM reasoning with ML forecasting. It uses SageMaker XGBoost with 97.9% accuracy to predict demand."

**Show:**
- Forecast results
- Explain: "In production, this helps sellers optimize inventory and avoid stockouts"

---

### Demo 4: Architecture (60 seconds)

**Show:** Open `docs/ARCHITECTURE.md`

**Say:**
> "The architecture uses:
> - Bedrock Agent Core for autonomous orchestration
> - Nova Pro for reasoning
> - SageMaker for ML forecasting
> - S3, Glue, and Athena for the data platform
> - Lambda and EventBridge for scheduled runs
> 
> Everything is deployed with AWS CDK for reproducibility."

**Show:**
- Scroll through architecture diagram
- Point out key components

---

### Demo 5: Autonomous Execution (30 seconds)

**Show:** Open `infra/stacks/agent_stack.py` (line ~120)

**Say:**
> "MERLIN runs autonomously every 6 hours via EventBridge, analyzing performance and suggesting optimizations. It can execute actions with human-in-the-loop approval."

**Show:**
```python
self.event_rule = events.Rule(
    self,
    "ScheduledAgentRun",
    schedule=events.Schedule.rate(Duration.hours(6)),
)
```

---

### Closing (30 seconds)

**Say:**
> "To summarize, MERLIN meets all hackathon requirements:
> - ✅ Uses reasoning LLMs (Nova Pro + Claude)
> - ✅ Bedrock Agent Core with action groups
> - ✅ Autonomous capabilities
> - ✅ Multi-platform support for 30M+ sellers
> - ✅ Production-ready with full AWS infrastructure
> 
> The code is open source on GitHub. Thank you!"

**Show:**
- GitHub repo
- README with setup instructions

---

## 🎥 Recording Tips

### Tools
- **Mac:** QuickTime (free) or Loom
- **Windows:** OBS Studio (free) or Loom
- **Online:** Loom.com (free for 5 min videos)

### Settings
- **Resolution:** 1920x1080 (1080p)
- **Frame rate:** 30 fps
- **Audio:** Clear microphone, no background noise
- **Length:** 3-5 minutes (judges prefer concise)

### Best Practices
1. **Script it:** Write out what you'll say
2. **Practice:** Do a dry run first
3. **Show, don't tell:** Demonstrate features live
4. **Highlight uniqueness:** Multi-platform support
5. **Be enthusiastic:** Show passion for the project
6. **End strong:** Recap key points

---

## 📤 Upload & Share

### YouTube (Recommended)
```bash
# 1. Upload to YouTube
# 2. Set to "Unlisted" (judges can access, not public)
# 3. Add to video description:
#    - GitHub repo link
#    - Live demo link (if deployed)
#    - Architecture diagram link
```

### Loom
```bash
# 1. Record with Loom
# 2. Get shareable link
# 3. Add to README
```

### Add to README
```markdown
## 🎬 Demo Video

**Watch the full demo:** [YouTube Link](https://youtube.com/...)

**Live Demo:** [AWS App Runner](https://xxxxx.awsapprunner.com)

**GitHub:** [Repository](https://github.com/...)
```

---

## 📊 What to Emphasize

### Technical Excellence
- Bedrock Agent Core implementation
- Nova Pro reasoning
- Multi-platform architecture
- Production-ready infrastructure

### Business Value
- 30M+ sellers addressable market (vs 2.5M Amazon-only)
- Multi-platform = higher value proposition
- Real pain point solved

### Innovation
- Hybrid intelligence (LLM + ML)
- Marketplace-agnostic design
- Autonomous execution with guardrails

---

## ✅ Checklist Before Recording

- [ ] Streamlit UI running locally
- [ ] Sample data loaded
- [ ] AWS credentials configured
- [ ] Browser at localhost:8501
- [ ] Architecture diagrams ready
- [ ] Script prepared
- [ ] Recording software tested
- [ ] Microphone working
- [ ] No notifications/distractions

---

## 🎯 Alternative: Live Demo

If you prefer live demo over video:

1. **Deploy UI to AWS App Runner**
   ```bash
   ./deploy_ui.sh
   ```

2. **Share URL with judges**
   - Add to Devpost submission
   - Add to README
   - Test thoroughly before sharing

3. **Prepare backup video**
   - In case live demo has issues
   - Shows full functionality

---

Good luck! 🚀
