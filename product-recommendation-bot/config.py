import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant")
    APP_TENANT_ID = os.environ.get("MicrosoftAppTenantId", "")
    
    # Added to support interaction with Azure AI Language API
    LANGUAGE_API_ENDPOINT = os.environ.get("LanguageApiEndpoint", "")
    LANGUAGE_API_KEY = os.environ.get("LanguageApiKey", "")

    # Gemini Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD_9mYPY7gFm--DgjFV0QZYXUJ5Y7J6imY")
    
    # Google Custom Search Configuration
    GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY", "AIzaSyAz-lJLZBA-5tFZ1vWfgZew4Crc0s8yPQE")
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "a67b9550da4c04a5b")
    
    # Local Mode Configuration
    USE_LOCAL_MODE = os.environ.get("USE_LOCAL_MODE", "false").lower() == "true"
    LOCAL_LLM_MODEL = os.environ.get("LOCAL_LLM_MODEL", "llama3.2:3b")
    
    # Data Configuration (deprecated - using web search now)
    DATA_FILE_PATH = os.environ.get("DATA_FILE_PATH", "bots/Product Review Data.csv")
