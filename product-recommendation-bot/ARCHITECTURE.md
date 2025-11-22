# Product Recommendation Chatbot - Architecture

## System Overview

The Product Recommendation Chatbot is a modular system that supports both **Cloud Mode** and **Local Mode** for product recommendations based on expert reviews.

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface"
        UI[Gradio Web UI<br/>Port 7861]
    end
    
    subgraph "Core Application"
        APP[ProductRecommendationChatbot<br/>gradio_app.py]
        CONFIG[Configuration<br/>config.py]
        ENV[.env File]
    end
    
    subgraph "Cloud Mode Components"
        GEMINI[Google Gemini API<br/>gemini-2.5-flash]
        GSEARCH[Google Custom Search API]
    end
    
    subgraph "Local Mode Components"
        OLLAMA[Ollama LLM<br/>llama3.2:3b]
        SCRAPER[Web Scraper<br/>DuckDuckGo + BeautifulSoup]
    end
    
    subgraph "External Resources"
        REVIEW_SITES[Review Sites<br/>Wirecutter, RTINGS,<br/>Consumer Reports, etc.]
    end
    
    UI <--> APP
    APP --> CONFIG
    CONFIG --> ENV
    
    APP -->|Cloud Mode| GEMINI
    APP -->|Cloud Mode| GSEARCH
    
    APP -->|Local Mode| OLLAMA
    APP -->|Local Mode| SCRAPER
    
    GSEARCH --> REVIEW_SITES
    SCRAPER --> REVIEW_SITES
```

---

## Detailed Component Architecture

```mermaid
graph LR
    subgraph "Initialization Flow"
        START([Application Start]) --> LOAD_ENV[Load .env File<br/>load_dotenv]
        LOAD_ENV --> IMPORT_CONFIG[Import DefaultConfig]
        IMPORT_CONFIG --> CHECK_MODE{USE_LOCAL_MODE?}
        
        CHECK_MODE -->|true| INIT_LOCAL[Initialize Local Mode<br/>LocalLLM + ReviewSiteScraper]
        CHECK_MODE -->|false| INIT_CLOUD[Initialize Cloud Mode<br/>Gemini + Google Search]
        
        INIT_LOCAL --> TEST_OLLAMA{Ollama<br/>Available?}
        TEST_OLLAMA -->|Yes| READY_LOCAL[✓ Ready - Local Mode]
        TEST_OLLAMA -->|No| WARN[⚠️ Warning: Ollama Not Running]
        
        INIT_CLOUD --> READY_CLOUD[✓ Ready - Cloud Mode]
        
        READY_LOCAL --> LAUNCH[Launch Gradio UI]
        READY_CLOUD --> LAUNCH
        WARN --> LAUNCH
    end
```

---

## Request Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant GradioUI
    participant Chatbot
    participant SearchEngine
    participant LLM
    participant ReviewSites
    
    User->>GradioUI: Enter query<br/>"Best wireless headphones under $200"
    GradioUI->>Chatbot: chat(message, history)
    
    Note over Chatbot: Extract price limit, brand, category
    
    Chatbot->>Chatbot: Build search query<br/>"best wireless headphones under $200 2024"
    
    alt Cloud Mode
        Chatbot->>SearchEngine: Google Custom Search API
        SearchEngine->>ReviewSites: Search expert reviews
        ReviewSites-->>SearchEngine: Return results
        SearchEngine-->>Chatbot: Search results (JSON)
    else Local Mode
        Chatbot->>SearchEngine: DuckDuckGo Web Scraper
        SearchEngine->>ReviewSites: Scrape review sites
        ReviewSites-->>SearchEngine: HTML content
        SearchEngine-->>Chatbot: Parsed results (JSON)
    end
    
    Note over Chatbot: Extract product info from results
    
    alt Cloud Mode
        Chatbot->>LLM: Gemini API<br/>Extract products from snippets
        LLM-->>Chatbot: Structured product data
    else Local Mode
        Chatbot->>LLM: Ollama (llama3.2:3b)<br/>Extract products from snippets
        LLM-->>Chatbot: Structured product data
    end
    
    Note over Chatbot: Generate personalized response
    
    alt Cloud Mode
        Chatbot->>LLM: Gemini API<br/>Generate recommendation
        LLM-->>Chatbot: Formatted response
    else Local Mode
        Chatbot->>LLM: Ollama<br/>Generate recommendation
        LLM-->>Chatbot: Formatted response
    end
    
    Chatbot-->>GradioUI: Response with product list
    GradioUI-->>User: Display recommendations
```

---

## Data Flow Architecture

```mermaid
graph TD
    subgraph "Input Processing"
        INPUT[User Query] --> PARSE[Query Parser]
        PARSE --> EXTRACT_PRICE[Extract Price Limit]
        PARSE --> EXTRACT_BRAND[Extract Brand]
        PARSE --> DETECT_CAT[Detect Category]
    end
    
    subgraph "Search Strategy"
        DETECT_CAT --> CATEGORY{Category}
        CATEGORY -->|Electronics| SITES_TECH[Wirecutter, RTINGS]
        CATEGORY -->|Home| SITES_HOME[Consumer Reports,<br/>Good Housekeeping]
        CATEGORY -->|Fashion| SITES_FASHION[WhoWhatWear, Vogue]
    end
    
    subgraph "Search Execution"
        SITES_TECH --> SEARCH_ENGINE[Search Engine<br/>Cloud or Local]
        SITES_HOME --> SEARCH_ENGINE
        SITES_FASHION --> SEARCH_ENGINE
        
        SEARCH_ENGINE --> CACHE{In Cache?}
        CACHE -->|Yes| CACHED_RESULTS[Return Cached Results]
        CACHE -->|No| FETCH[Fetch New Results]
        FETCH --> STORE_CACHE[Store in Cache]
        STORE_CACHE --> RESULTS[Search Results]
        CACHED_RESULTS --> RESULTS
    end
    
    subgraph "Product Extraction"
        RESULTS --> LLM_EXTRACT[LLM: Extract Products<br/>from Snippets]
        LLM_EXTRACT --> PRODUCTS[Structured Product List<br/>name, price, pros, source]
    end
    
    subgraph "Response Generation"
        PRODUCTS --> CONTEXT[Build Context<br/>user preferences, budget]
        CONTEXT --> LLM_GEN[LLM: Generate<br/>Personalized Response]
        LLM_GEN --> FORMAT[Format with Product Details]
        FORMAT --> OUTPUT[Final Response]
    end
```

---

## Class Structure

```mermaid
classDiagram
    class ProductRecommendationChatbot {
        -config: DefaultConfig
        -use_local: bool
        -conversation_history: list
        -search_cache: dict
        -user_state: dict
        -llm: LocalLLM or None
        -scraper: ReviewSiteScraper or None
        +__init__(use_local)
        +chat(message, history)
        -_web_search_products(query)
        -_build_search_query(query)
        -_detect_category(query)
        -_google_custom_search(query)
        -_extract_products_from_results(results, query)
        -_extract_product_info_with_gemini(title, snippet, link, query)
        -_call_gemini_api(prompt)
        -_generate_response(query, products)
        -_extract_price_limit(query)
        -_extract_brand(query)
    }
    
    class DefaultConfig {
        +PORT: int
        +GEMINI_API_KEY: str
        +GOOGLE_SEARCH_API_KEY: str
        +GOOGLE_SEARCH_ENGINE_ID: str
        +USE_LOCAL_MODE: bool
        +LOCAL_LLM_MODEL: str
    }
    
    class LocalLLM {
        -model: str
        -base_url: str
        +__init__(model, base_url)
        +generate(prompt, temperature, max_tokens)
        +extract_json(prompt)
        +test_connection()
    }
    
    class ReviewSiteScraper {
        -headers: dict
        -cache: dict
        +__init__()
        +search(query, sites, max_results)
        -_search_site(site, query)
        +get_sites_for_category(category)
    }
    
    ProductRecommendationChatbot --> DefaultConfig
    ProductRecommendationChatbot --> LocalLLM : uses in local mode
    ProductRecommendationChatbot --> ReviewSiteScraper : uses in local mode
```

---

## Mode Comparison

| Feature | Cloud Mode | Local Mode |
|---------|-----------|------------|
| **LLM** | Google Gemini API (gemini-2.5-flash) | Ollama (llama3.2:3b) |
| **Search** | Google Custom Search API | DuckDuckGo Web Scraper |
| **Cost** | API usage fees | Free (local compute) |
| **Speed** | Fast (cloud infrastructure) | Moderate (local hardware) |
| **Privacy** | Data sent to Google | Fully private |
| **Dependencies** | API keys required | Ollama + beautifulsoup4 + lxml |
| **Internet** | Required | Required (for scraping) |
| **Rate Limits** | API quotas apply | No limits |

---

## Configuration Flow

```mermaid
graph LR
    subgraph "Environment Setup"
        ENV_FILE[.env File] --> DOTENV[load_dotenv]
        DOTENV --> OS_ENV[OS Environment Variables]
    end
    
    subgraph "Configuration Loading"
        OS_ENV --> CONFIG_CLASS[DefaultConfig Class]
        CONFIG_CLASS --> PARSE_BOOL{Parse USE_LOCAL_MODE<br/>.lower == 'true'}
        PARSE_BOOL --> MODE_FLAG[use_local: bool]
    end
    
    subgraph "Mode Selection"
        MODE_FLAG --> CHECK{use_local?}
        CHECK -->|true| LOCAL_INIT[Initialize:<br/>LocalLLM<br/>ReviewSiteScraper]
        CHECK -->|false| CLOUD_INIT[Use:<br/>Gemini API<br/>Google Search API]
    end
    
    style ENV_FILE fill:#e1f5ff
    style MODE_FLAG fill:#fff4e1
    style LOCAL_INIT fill:#e8f5e9
    style CLOUD_INIT fill:#fff3e0
```

---

## Technology Stack

### Frontend
- **Gradio 4.44+**: Web UI framework with chat interface
- **Custom CSS**: Light theme with off-white background and red accents

### Backend (Cloud Mode)
- **Google Gemini API**: LLM for product extraction and response generation
- **Google Custom Search API**: Search expert review sites
- **Python Requests**: HTTP client for API calls

### Backend (Local Mode)
- **Ollama**: Local LLM server (llama3.2:3b model)
- **BeautifulSoup4**: HTML parsing for web scraping
- **lxml**: XML/HTML parser
- **DuckDuckGo**: Search engine (no API key required)

### Common Components
- **python-dotenv**: Environment variable management
- **Python 3.8+**: Runtime environment

---

## File Structure

```
product-recommendation-bot/
├── gradio_app.py          # Main application & UI
├── config.py              # Configuration management
├── local_llm.py           # Ollama LLM interface
├── web_scraper.py         # Web scraping for local mode
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (gitignored)
├── .env.example           # Example environment file
├── run.bat                # Windows launch script
├── README.md              # Project documentation
├── API_KEYS_GUIDE.md      # API setup instructions
└── TEAM_SETUP.md          # Team collaboration guide
```

---

## Key Design Decisions

### 1. **Modular Architecture**
- Clean separation between cloud and local components
- Easy to switch modes via configuration
- No code changes required to toggle modes

### 2. **Import Order Fix**
- `load_dotenv()` called **before** importing `DefaultConfig`
- Ensures environment variables are available when class variables are evaluated
- Critical for proper mode selection

### 3. **Caching Strategy**
- Search results cached to reduce API calls/scraping
- Rate limiting (2-second delay) for API requests
- Improves performance and respects rate limits

### 4. **Category-Based Site Selection**
- Different review sites for different product categories
- Electronics → Wirecutter, RTINGS
- Home → Consumer Reports, Good Housekeeping
- Fashion → WhoWhatWear, Vogue

### 5. **Graceful Degradation**
- Local mode warns if Ollama not running but doesn't crash
- Continues to function with available components
- User-friendly error messages

---

## Deployment Considerations

### Cloud Mode Requirements
1. Google Gemini API key
2. Google Custom Search API key + Search Engine ID
3. Internet connection
4. API quota management

### Local Mode Requirements
1. Ollama installed and running (`ollama serve`)
2. Model downloaded (`ollama pull llama3.2:3b`)
3. Python packages: `beautifulsoup4`, `lxml`
4. Internet connection (for web scraping)

### Running the Application
```bash
# Windows
.\run.bat

# Direct Python
python gradio_app.py
```

The application will automatically detect the mode based on `USE_LOCAL_MODE` in `.env` and initialize the appropriate components.
