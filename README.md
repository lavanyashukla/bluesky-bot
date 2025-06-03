# I Wonder Social-Bot Showdown 🤖

> One Twitter/X handle, five self-improving bots, emoji-signed shifts.

**Goal**: Reach 1,000 followers while teaching the audience how each AI improvement loop works in real-time.

## 🎯 The Bots

| Bot Type | Emoji | Description | Improvement Method |
|----------|-------|-------------|-------------------|
| Self-Refine | 🪲 | Draft → self-critique → rewrite | Every post |
| DPO | 👾 | A/B test tweets, mini-LoRA after +5 likes delta | Continuous |
| RLAIF | 🐾 | GPT-4o judge scores with PPO updates | Every 3 drafts |
| Mind-Pool | 🦕 | 6 personas compete, top-2 survive | Every 50 impressions |
| DevOps Self-Fix | 🦍 | Monitors & auto-patches other bots | Every 60s |

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   cp config/bot_config.example.json config/bot_config.json
   # Add your API keys to bot_config.json
   ```

2. **Run the Orchestrator**
   ```bash
   python scripts/orchestrator.py
   ```

3. **View Dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

## 📁 Project Structure

```
├── config/              # Configuration files
├── scripts/             # Core bot implementations
├── notebooks/           # Educational Jupyter notebooks
├── dashboard/           # Streamlit monitoring dashboard
├── episode_assets/      # Generated assets and visualizations
└── tests/              # Unit tests
```

## 📊 Success Metrics

- **Reach**: 1,000 followers in ≤ 7 days
- **Clarity**: 80% can identify which bot posted what
- **Learning**: 50% can apply ≥ 2 improvement loops
- **DIY**: 250 GitHub stars in 30 days

## 🔧 Architecture

Each bot runs as a microservice, coordinated by the orchestrator. The DevOps bot monitors all others and auto-fixes issues through PRs and redeployments.

---

*Built for busy tech leaders who want intuition, not code dumps.* 