# AI-Powered Product Recommendation Chatbot

An intelligent conversational AI that provides expert-backed product recommendations using Retrieval-Augmented Generation (RAG).

## Features

- **Smart Category Detection**: Automatically detects product categories and searches appropriate review sites
  - **Electronics**: Wirecutter, RTINGS
  - **Home Goods**: Consumer Reports, Good Housekeeping  
  - **Fashion**: Who What Wear, Vogue

- **RAG Architecture**: Retrieves live expert reviews, extracts product data with AI, generates personalized recommendations

- **Conversational Memory**: Remembers user preferences (brand, price range) across conversation

- **Modern UI**: Clean Gradio web interface with accessibility features

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file:
```
GEMINI_API_KEY=gemini_api
GOOGLE_SEARCH_API_KEY=google_search_api_key
GOOGLE_SEARCH_ENGINE_ID=search_engine_id
```

### 3. Run the Chatbot

**Option A: Using the run script (Easiest)**
```bash
run.bat
```

**Option B: Using conda environment directly**
```bash
C:\Users\shash\anaconda3\envs\MSAI631-MBF\python.exe gradio_app.py
```

**Option C: Activate conda environment first**
```bash
conda activate MSAI631-MBF
python gradio_app.py
```

Open your browser to: **http://127.0.0.1:7860**

## Example Queries

- "Best wireless headphones under $200"
- "Affordable laptop for students"
- "Best vacuum cleaner for pet hair"
- "Stylish winter boots for women"

## Project Structure

```
product-recommendation-bot/
├── gradio_app.py          # Main Gradio UI application
├── config.py              # Configuration and API keys
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not in git)
└── README.md             # This file
```

## Technical Stack

- **AI Model**: Google Gemini 2.5 Flash
- **Search**: Google Custom Search API
- **UI Framework**: Gradio 4.44+
- **Language**: Python 3.8+

## Category-Specific Sites

The bot automatically selects review sites based on product category:

| Category | Review Sites |
|----------|-------------|
| Electronics | Wirecutter, RTINGS |
| Home Goods | Consumer Reports, Good Housekeeping |
| Fashion | Who What Wear, Vogue |

## API Usage

- **Google Custom Search**: 100 queries/day (free tier)
- **Google Gemini**: Free tier available
- **Rate Limiting**: 2-second delay between searches
- **Caching**: Search results cached to conserve quota

## Course Project

This is a Human-Computer Interaction course project demonstrating:
- Conversational AI interfaces
- Retrieval-Augmented Generation (RAG)
- Natural language interaction
- Accessible web design

## License

Educational project for MSAI 631 - Human-Computer Interaction
