# 🚀 Deploy Bot Showdown to Railway

## Why Railway?
- ✅ **Free tier** for personal projects ($5/month credit)
- ✅ **Auto-deploy** from GitHub pushes
- ✅ **Environment variables** for secrets
- ✅ **Multiple services** (bot + dashboard)
- ✅ **Built-in databases** and persistent storage

---

## 📋 **Pre-Deployment Checklist**

### 1. **Test Locally First**
```bash
# Make sure bot works locally
python3 run_bot.py

# Test dashboard  
python3 run_dashboard.py
```

### 2. **Commit to Git**
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

---

## 🎯 **Deploy to Railway**

### **Step 1: Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your repository

### **Step 2: Create New Project**
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your `jun2-blog` repository
4. Railway will auto-detect Python and install dependencies

### **Step 3: Configure Environment Variables**
In Railway dashboard → **Variables** tab, add:

```bash
# Bluesky Configuration
BLUESKY_HANDLE=thephillip.bsky.social
BLUESKY_APP_PASSWORD=xxwx-ko5f-aqwf-3qrz

# OpenAI Configuration  
OPENAI_API_KEY=your-openai-api-key

# Service Configuration
SERVICE_TYPE=bot
# Set to 'bot' for orchestrator or 'dashboard' for web interface

# Bot Configuration (Optional)
BOT_INTERVAL_MINUTES=30
MAX_POSTS_PER_DAY=48

# W&B Configuration (Optional)
WANDB_API_KEY=your-wandb-key
WANDB_PROJECT=bluesky-bot-showdown
```

### **Step 4: Configure Startup Command**
In Railway dashboard → **Settings** → **Deploy**:

**Start Command:** `python3 start.py`

### **Step 5: Deploy Bot Service**
1. Set `SERVICE_TYPE=bot` in environment variables
2. Click **Deploy**
3. Bot will start posting every 30 minutes! 🎉

---

## 📊 **Add Dashboard Service (Optional)**

### **Create Second Service**
1. In Railway project, click **"+ New"**
2. Select **"GitHub Repo"** (same repo)
3. Configure environment variables:
   - Copy all variables from bot service
   - **Change:** `SERVICE_TYPE=dashboard`
4. Deploy second service

### **Access Dashboard**
Railway will provide a public URL like:
`https://your-app-name.railway.app`

---

## 🔍 **Monitor Your Deployment**

### **Railway Logs**
- View real-time logs in Railway dashboard
- Monitor bot posts and any errors

### **W&B Dashboard**
- Visit your W&B project URL
- Track post generation in real-time
- See improvement analytics

### **Bluesky Account**
- Check your Bluesky feed for new posts
- Monitor follower growth

---

## 🛠 **Troubleshooting**

### **Common Issues**

1. **Import Errors**
   - Check logs for Python path issues
   - Ensure all dependencies in `requirements.txt`

2. **API Key Errors**
   - Verify environment variables in Railway
   - Check Bluesky app password is correct

3. **Database Issues**
   - Railway provides persistent storage
   - SQLite files persist between deployments

4. **Memory/CPU Limits**
   - Free tier: 512MB RAM, 1 vCPU
   - Should be sufficient for this bot

### **Get Deployment Logs**
```bash
# If you have Railway CLI installed
railway logs
```

---

## 💰 **Cost Estimation**

### **Railway Free Tier**
- **$5/month** credit (plenty for this bot)
- **Sleeps after 30min inactivity** (we disable this)
- **500GB bandwidth/month**

### **Estimated Usage**
- **Bot Service:** ~$2-3/month
- **Dashboard Service:** ~$1-2/month  
- **Total:** Well within free tier!

---

## 🎉 **What Happens After Deploy**

1. **Bot posts every 30 minutes** automatically
2. **W&B logs** all post generation details
3. **Database stores** post history and metrics
4. **Dashboard shows** real-time progress (if deployed)
5. **Auto-restarts** if any issues occur

Your bot is now **running 24/7 in the cloud!** 🚀

---

## 🔄 **Updates and Maintenance**

### **Deploy Updates**
```bash
git add .
git commit -m "Update bot logic"
git push origin main
# Railway auto-deploys! ✨
```

### **Monitor Performance**
- Check Railway dashboard regularly
- Review W&B analytics
- Monitor Bluesky follower growth

---

## 📞 **Need Help?**

- **Railway Docs:** [docs.railway.app](https://docs.railway.app)
- **Railway Discord:** Great community support
- **Project Issues:** Check GitHub issues

**Your Bot Showdown is now live! 🎊** 