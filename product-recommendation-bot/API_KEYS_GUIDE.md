# API Keys Setup Guide

This guide will help you obtain your own API keys for the Product Recommendation Chatbot.

---

## Required API Keys

You need two sets of API keys:
1. **Google Gemini API Key** (for AI-powered recommendations)
2. **Google Custom Search API Key + Search Engine ID** (for web search)

---

## Google Gemini API Key

### Step 1: Go to Google AI Studio
Visit: https://aistudio.google.com/app/apikey

### Step 2: Sign in with Google Account
Use your personal or university Google account.

### Step 3: Create API Key
1. Click **"Get API Key"** or **"Create API Key"**
2. Select **"Create API key in new project"** (or use existing project)
3. Copy the generated API key (starts with `AIza...`)

### Step 4: Save the Key
```
GEMINI_API_KEY=AIzaSy...your_key_here
```

### Free Tier Limits:
- Free to use
- 60 requests per minute
- Sufficient for development and testing

---

## Google Custom Search API

### Part A: Get the API Key

#### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/

#### Step 2: Create a New Project (if needed)
1. Click the project dropdown at the top
2. Click **"New Project"**
3. Name it (e.g., "Product-Recommendation-Bot")
4. Click **"Create"**

#### Step 3: Enable Custom Search API
1. Go to: https://console.cloud.google.com/apis/library
2. Search for **"Custom Search API"**
3. Click on it
4. Click **"Enable"**

#### Step 4: Create API Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials"** → **"API Key"**
3. Copy the generated API key
4. (Optional) Click **"Restrict Key"** and limit it to "Custom Search API" only

### Part B: Create Custom Search Engine

#### Step 1: Go to Programmable Search Engine
Visit: https://programmablesearchengine.google.com/

#### Step 2: Create New Search Engine
1. Click **"Add"** or **"Create a new search engine"**
2. **Search engine name**: "Product Reviews Search"
3. **What to search**: Select **"Search specific sites"**

#### Step 3: Add Review Sites
Add these sites (one per line):
```
wirecutter.com
rtings.com
consumerreports.org
goodhousekeeping.com
whowhatwear.com
vogue.com
techradar.com
```

#### Step 4: Configure Settings
1. Click **"Create"**
2. On the next page, click **"Customize"**
3. Turn ON **"Search the entire web"** (optional, for broader results)
4. Under **"Sites to search"**, ensure your review sites are listed

#### Step 5: Get Search Engine ID
1. In the **"Overview"** or **"Setup"** tab
2. Find **"Search engine ID"** (looks like: `a67b9550da4c04a5b`)
3. Copy this ID

### Save Both Keys:
```
GOOGLE_SEARCH_API_KEY=AIza...your_api_key_here
GOOGLE_SEARCH_ENGINE_ID=a67b9550da4c04a5b
```

### Free Tier Limits:
- **100 search queries per day** (free)
- After 100 queries, you'll need to wait 24 hours or upgrade
- The chatbot has built-in rate limiting and caching to conserve quota

---

## Create Your `.env` File

In the `product-recommendation-bot/` folder, create a file named `.env`:

```
GEMINI_API_KEY=AIzaSy...your_gemini_key
GOOGLE_SEARCH_API_KEY=AIza...your_search_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

**Important:**
- No quotes around the values
- No spaces around the `=` sign
- Keep this file private (it's in `.gitignore`)

---

## Verify Setup

Run the chatbot:
```bash
python gradio_app.py
```

If you see:
```
Running on local URL:  http://127.0.0.1:7861
```
**Success!** Your API keys are working.

If you see errors:
- `403 Forbidden` → Check your Gemini API key
- `API key not valid` → Check your Google Search API key
- `No results found` → Check your Search Engine ID

---

## Cost Breakdown

| Service | Free Tier | Cost After Free Tier |
|---------|-----------|---------------------|
| **Gemini API** | 60 req/min | Free (as of Nov 2024) |
| **Custom Search** | 100 queries/day | $5 per 1000 queries |

**For this project:** You should stay within free tier limits during development.

---

## Security Best Practices

1. **Never commit `.env` to Git** (already in `.gitignore`)
2. **Don't share your API keys** in screenshots or documentation
3. **Regenerate keys** if accidentally exposed
4. **Use API restrictions** in Google Cloud Console to limit usage

---

## roubleshooting

### "Custom Search API not enabled"
1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Custom Search API"
3. Click "Enable"

### "Search Engine ID not found"
1. Go to: https://programmablesearchengine.google.com/
2. Click on your search engine
3. Copy the ID from the "Setup" or "Overview" tab

### "Quota exceeded"
- Wait 24 hours for quota reset
- Or upgrade to paid tier in Google Cloud Console

---

## Need Help?

- **Gemini API Docs**: https://ai.google.dev/docs
- **Custom Search Docs**: https://developers.google.com/custom-search/v1/overview
- **Google Cloud Console**: https://console.cloud.google.com/

---

## Estimated Setup Time

- **Gemini API**: 2-3 minutes
- **Custom Search API**: 5-10 minutes
- **Total**: ~15 minutes

Once you have your keys, you're ready to run the chatbot! 🎉
