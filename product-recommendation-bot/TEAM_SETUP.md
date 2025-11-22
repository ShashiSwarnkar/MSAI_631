
### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- API Keys (you'll need to share these securely)

---

## Step-by-Step Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <your-github-repo-url>
cd MSAI_631/product-recommendation-bot
```

### Step 2: Install Python Dependencies

**Option A: Using pip (Recommended for simplicity)**
```bash
pip install -r requirements.txt
```

**Option B: Using conda (If they have Anaconda)**
```bash
conda create -n product-bot python=3.8
conda activate product-bot
pip install -r requirements.txt
```

### Step 3: Get Your Own API Keys

**Follow the detailed guide:** [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)

**Quick Summary:**
1. **Gemini API Key**: Visit https://aistudio.google.com/app/apikey
2. **Google Custom Search**: 
   - API Key: https://console.cloud.google.com/apis/credentials
   - Search Engine ID: https://programmablesearchengine.google.com/

Once you have your keys, create a `.env` file:

```
GEMINI_API_KEY=<your_gemini_api_key>
GOOGLE_SEARCH_API_KEY=<your_google_search_api_key>
GOOGLE_SEARCH_ENGINE_ID=<your_search_engine_id>
```

### Step 4: Run the Application

**Windows:**
```bash
python gradio_app.py
```

**Mac/Linux:**
```bash
python3 gradio_app.py
```

### Step 5: Access the UI

Open your browser to: **http://127.0.0.1:7861**

---

## Getting API Keys

**Each team member must create their own API keys.**

**See detailed instructions:** [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)

### Why Create Your Own Keys?
- **Security**: Keep your credentials private
- **Quota**: Each person gets their own 100 searches/day
- **Control**: Manage your own usage and billing
- **Best Practice**: Never share API keys

### Quick Links:
- Gemini API: https://aistudio.google.com/app/apikey
- Google Cloud Console: https://console.cloud.google.com/
- Custom Search Engine: https://programmablesearchengine.google.com/

### Files to Include in Git Repository:
- `gradio_app.py`
- `config.py`
- `requirements.txt`
- `README.md`
- `run.bat` (Windows users)
- `.gitignore` (to prevent committing `.env`)

### Files to EXCLUDE from Git:
- `.env` (contains sensitive API keys)
- `__pycache__/`
- `*.pyc`

### Create/Update `.gitignore`:
```
.env
__pycache__/
*.pyc
*.pyo
.DS_Store
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'gradio'"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 2: "Port 7861 already in use"
**Solution:** Change the port in `gradio_app.py` (line 472):
```python
demo.launch(share=False, server_name="127.0.0.1", server_port=7862)
```

### Issue 3: "API Key not found"
**Solution:** Ensure `.env` file exists in the correct folder with proper keys

### Issue 4: "Google Search API quota exceeded"
**Solution:** The free tier allows 100 searches/day. Wait 24 hours or upgrade the API plan.

---

## API Usage Limits

- **Google Custom Search**: 100 queries/day (free tier)
- **Google Gemini**: Free tier available (check current limits)
- **Rate Limiting**: Built-in 2-second delay between searches
- **Caching**: Results are cached to conserve quota

---

## Testing the Setup

Once running, try these test queries:

1. **Electronics**: "Best wireless headphones under $200"
2. **Home Goods**: "Best vacuum cleaner for pet hair"
3. **Fashion**: "Stylish winter boots"

You should see:
- Search status in terminal
- Results from appropriate review sites
- Product recommendations in the UI

---

### Team Collaboration

1. **Use Git branches** for new features
2. **Don't commit API keys** - use `.gitignore`
3. **Document changes** in commit messages
4. **Test locally** before pushing to main branch
5. **Share API quota** - coordinate testing to avoid exceeding limits

---

Check this guide first
2. Verify Python version: `python --version`
3. Verify dependencies: `pip list | grep gradio`
4. Check terminal output for error messages

---

## Local Mode (Optional)

The bot supports two modes:
- **Cloud Mode** (default): Uses Gemini API + Google Custom Search
- **Local Mode**: Uses Ollama (local LLM) + Web Scraping

### Why Use Local Mode?
- No API keys needed
- No quota limits
- Complete privacy
- Runs offline (after setup)

### Setup Local Mode

**1. Install Ollama**
- Download: https://ollama.com/download
- Restart computer after installation

**2. Download Model**
```bash
ollama pull llama3.2:3b
```

**3. Install Dependencies**
```bash
pip install beautifulsoup4 lxml
```

**4. Enable Local Mode**

Edit `.env` and add:
```
USE_LOCAL_MODE=true
```

**5. Restart Bot**

You should see: `🏠 Using LOCAL mode`

### Switching Modes

Edit `.env`:
- **Cloud**: `USE_LOCAL_MODE=false` (or omit)
- **Local**: `USE_LOCAL_MODE=true`

Then restart the bot.

### Local Mode Requirements
- 8GB+ RAM recommended
- 10GB disk space (for model)
- Slower than cloud (3-5s vs 1-2s)
