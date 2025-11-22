# 🤝 How to Share This Project with Your Team

## Quick Share Instructions

### Option 1: Share the Repository URL (Recommended)

Simply share this URL with your team members:

```
https://github.com/ShashiSwarnkar/MSAI_631
```

**Tell them to:**
1. Clone the repository
2. Navigate to `product-recommendation-bot/` folder
3. Follow the setup instructions in [TEAM_COLLABORATION_GUIDE.md](TEAM_COLLABORATION_GUIDE.md)

---

### Option 2: Add Team Members as Collaborators

If you want team members to have write access:

1. Go to your repository: https://github.com/ShashiSwarnkar/MSAI_631
2. Click **Settings** (top right)
3. Click **Collaborators** (left sidebar)
4. Click **Add people**
5. Enter their GitHub username or email
6. Select their permission level:
   - **Write**: Can push to the repository
   - **Read**: Can only clone and view

---

### Option 3: Share via Email/Slack/Teams

**Copy and send this message to your team:**

---

> **Subject: Product Recommendation Chatbot - Repository Access**
>
> Hi Team,
>
> I've set up our Product Recommendation Chatbot project on GitHub. Here's how to get started:
>
> **Repository**: https://github.com/ShashiSwarnkar/MSAI_631
>
> **Quick Start:**
> ```bash
> git clone https://github.com/ShashiSwarnkar/MSAI_631.git
> cd MSAI_631/product-recommendation-bot
> ```
>
> **Setup Guide**: Once cloned, open `TEAM_COLLABORATION_GUIDE.md` for complete setup instructions.
>
> **What you'll need:**
> - Python 3.8+
> - Git installed
> - (Optional) API keys for cloud mode OR Ollama for local mode
>
> **Documentation:**
> - Setup: `TEAM_COLLABORATION_GUIDE.md`
> - Architecture: `ARCHITECTURE.md`
> - API Keys: `API_KEYS_GUIDE.md`
>
> Let me know if you have any questions!

---

## 📋 What Your Team Will See

When they clone the repository, they'll have access to:

### ✅ Complete Documentation
- **TEAM_COLLABORATION_GUIDE.md** - Step-by-step setup
- **ARCHITECTURE.md** - System design and diagrams
- **API_KEYS_GUIDE.md** - How to get API keys
- **README.md** - Project overview

### ✅ All Source Code
- `gradio_app.py` - Main application
- `local_llm.py` - Local LLM interface
- `web_scraper.py` - Web scraping module
- `config.py` - Configuration management

### ✅ Configuration Templates
- `.env.example` - Environment variable template
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

### ✅ Helper Scripts
- `run.bat` - Windows launcher

---

## 🔐 Security Note

**Important**: The `.env` file (containing API keys) is **NOT** shared in the repository. Each team member must:
1. Copy `.env.example` to `.env`
2. Add their own API keys OR configure for local mode

This keeps API keys secure and prevents accidental exposure.

---

## 🎯 Team Member Checklist

Share this checklist with your team:

- [ ] Clone the repository
- [ ] Navigate to `product-recommendation-bot/` folder
- [ ] Read `TEAM_COLLABORATION_GUIDE.md`
- [ ] Set up Python environment (conda or venv)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Configure for Cloud Mode (with API keys) OR Local Mode (with Ollama)
- [ ] Test the application
- [ ] Create a test branch and make a small change
- [ ] Push to GitHub and create a Pull Request (for practice)

---

## 📞 Support for Team Members

If team members have issues, direct them to:

1. **TEAM_COLLABORATION_GUIDE.md** - Common issues section
2. **GitHub Issues** - Create an issue for bugs/questions
3. **Team Chat** - Your preferred communication channel

---

## 🚀 Next Steps

1. **Share the repository URL** with your team
2. **Add collaborators** (if needed) on GitHub
3. **Schedule a kickoff meeting** to walk through the setup
4. **Create a team communication channel** (Slack, Discord, Teams)
5. **Set up project board** on GitHub for task tracking

---

## 📊 Repository Stats

- **URL**: https://github.com/ShashiSwarnkar/MSAI_631
- **Project**: `product-recommendation-bot/`
- **Language**: Python 3.8+
- **Framework**: Gradio 4.44+
- **Modes**: Cloud (Gemini) & Local (Ollama)

---

**Ready to collaborate! 🎉**
