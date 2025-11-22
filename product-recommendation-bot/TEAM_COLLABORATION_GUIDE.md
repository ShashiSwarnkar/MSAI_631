# Team Collaboration Guide
## Product Recommendation Chatbot

This guide will help your team members clone and set up the project on their local machines.

---

## 📦 Repository Information

**Repository URL**: `https://github.com/ShashiSwarnkar/MSAI_631.git`

**Project Path**: `product-recommendation-bot/`

---

## 🚀 Quick Start for Team Members

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/ShashiSwarnkar/MSAI_631.git

# Navigate to the project directory
cd MSAI_631/product-recommendation-bot
```

### Step 2: Set Up Python Environment

#### Option A: Using Conda (Recommended)

```bash
# Create a new conda environment
conda create -n MSAI631-MBF python=3.8

# Activate the environment
conda activate MSAI631-MBF

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred text editor
# Add your API keys or configure for local mode
```

**For Cloud Mode**, add to `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
USE_LOCAL_MODE=false
```

**For Local Mode**, add to `.env`:
```env
USE_LOCAL_MODE=true
LOCAL_LLM_MODEL=llama3.2:3b
```

### Step 4: Set Up Local Mode (Optional)

If using local mode, install and configure Ollama:

#### Windows:
```bash
# Download Ollama from https://ollama.ai/download
# Install and run

# Pull the required model
ollama pull llama3.2:3b

# Verify Ollama is running
ollama list
```

#### Mac/Linux:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull llama3.2:3b

# Start Ollama (if not running)
ollama serve
```

### Step 5: Run the Application

#### Windows:
```bash
.\run.bat
```

#### Mac/Linux:
```bash
python gradio_app.py
```

The application will be available at: **http://127.0.0.1:7861**

---

## 📋 Project Structure

```
product-recommendation-bot/
├── gradio_app.py              # Main application
├── config.py                  # Configuration management
├── local_llm.py               # Ollama LLM interface (local mode)
├── web_scraper.py             # Web scraping (local mode)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (NOT in Git)
├── .env.example               # Example environment file
├── .gitignore                 # Git ignore rules
├── run.bat                    # Windows launcher
├── README.md                  # Project overview
├── ARCHITECTURE.md            # System architecture
├── API_KEYS_GUIDE.md          # API setup instructions
├── TEAM_SETUP.md              # Detailed setup guide
└── TEAM_COLLABORATION_GUIDE.md # This file
```

---

## 🔑 Getting API Keys (Cloud Mode)

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key to your `.env` file

### Google Custom Search API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Custom Search API"
3. Create credentials → API Key
4. Copy to `.env` file

### Google Search Engine ID
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Create a new search engine
3. Configure to search the entire web
4. Copy the Search Engine ID to `.env`

See [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) for detailed instructions.

---

## 🔄 Git Workflow for Team

### Daily Workflow

```bash
# 1. Pull latest changes before starting work
git pull origin main

# 2. Create a new branch for your feature
git checkout -b feature/your-feature-name

# 3. Make your changes and test locally

# 4. Stage your changes
git add .

# 5. Commit with a descriptive message
git commit -m "Add: description of your changes"

# 6. Push your branch to GitHub
git push origin feature/your-feature-name

# 7. Create a Pull Request on GitHub
# Go to https://github.com/ShashiSwarnkar/MSAI_631
# Click "Pull Requests" → "New Pull Request"
```

### Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: new feature or file`
- `Fix: bug fix`
- `Update: changes to existing code`
- `Refactor: code restructuring`
- `Docs: documentation changes`
- `Style: formatting changes`

**Examples:**
```bash
git commit -m "Add: local mode support with Ollama"
git commit -m "Fix: environment variable loading order"
git commit -m "Update: improve search query building"
git commit -m "Docs: add architecture diagrams"
```

### Syncing with Main Branch

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Switch back to your feature branch
git checkout feature/your-feature-name

# Merge main into your branch
git merge main

# Resolve any conflicts if they occur
# Then push the updated branch
git push origin feature/your-feature-name
```

---

## 🧪 Testing Your Setup

### Test Cloud Mode

1. Set `USE_LOCAL_MODE=false` in `.env`
2. Add your API keys
3. Run the application
4. You should see: `☁️ Using CLOUD mode (Gemini + Google Custom Search)`
5. Try a query: "Best wireless headphones under $200"

### Test Local Mode

1. Set `USE_LOCAL_MODE=true` in `.env`
2. Ensure Ollama is running with `llama3.2:3b` model
3. Run the application
4. You should see: `🏠 Using LOCAL mode (Ollama + Web Scraping)`
5. Try a query: "Best laptop for students"

---

## 🐛 Common Issues & Solutions

### Issue: "Local modules not available"
**Solution**: Install dependencies
```bash
pip install beautifulsoup4 lxml
```

### Issue: "Ollama not running"
**Solution**: Start Ollama
```bash
# Windows: Run Ollama from Start Menu
# Mac/Linux:
ollama serve
```

### Issue: "Model not found"
**Solution**: Pull the model
```bash
ollama pull llama3.2:3b
```

### Issue: "API key invalid"
**Solution**: 
- Check your `.env` file has correct keys
- Ensure no extra spaces or quotes around keys
- Verify keys are active in Google Cloud Console

### Issue: "Module not found" errors
**Solution**: Ensure you're in the correct environment
```bash
# Conda
conda activate MSAI631-MBF

# venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Issue: "Port 7861 already in use"
**Solution**: Kill the existing process or change the port in `gradio_app.py`

---

## 📚 Additional Resources

- **Architecture Documentation**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Setup Guide**: [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)
- **Detailed Setup**: [TEAM_SETUP.md](TEAM_SETUP.md)
- **Project README**: [README.md](README.md)

---

## 👥 Team Communication

### Before Making Changes
1. Check existing issues and pull requests
2. Discuss major changes with the team
3. Create an issue for new features

### Code Review Process
1. All changes must go through Pull Requests
2. At least one team member should review
3. Address review comments before merging
4. Test locally before requesting review

### Branch Naming Convention
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-changed` - Documentation updates
- `refactor/what-changed` - Code refactoring

---

## 🔒 Security Best Practices

### ⚠️ NEVER commit these files:
- `.env` (contains API keys)
- Any file with credentials
- Large model files
- Personal configuration files

### ✅ Always:
- Use `.env.example` as a template
- Keep API keys in `.env` only
- Add sensitive files to `.gitignore`
- Review changes before committing

---

## 📞 Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review the documentation** in the repo
3. **Search existing issues** on GitHub
4. **Ask the team** in your communication channel
5. **Create a new issue** on GitHub with:
   - Description of the problem
   - Steps to reproduce
   - Error messages
   - Your environment (OS, Python version, mode)

---

## 🎯 Quick Reference Commands

```bash
# Clone repository
git clone https://github.com/ShashiSwarnkar/MSAI_631.git

# Setup environment
conda create -n MSAI631-MBF python=3.8
conda activate MSAI631-MBF
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run (Windows)
.\run.bat

# Run (Mac/Linux)
python gradio_app.py

# Git workflow
git pull origin main
git checkout -b feature/my-feature
git add .
git commit -m "Add: my feature"
git push origin feature/my-feature
```

---

## 📊 Repository Statistics

- **Language**: Python 3.8+
- **Framework**: Gradio 4.44+
- **Modes**: Cloud (Gemini) & Local (Ollama)
- **License**: Check repository for license information

---

**Happy Coding! 🚀**

For questions or issues, contact the repository maintainer or create an issue on GitHub.
