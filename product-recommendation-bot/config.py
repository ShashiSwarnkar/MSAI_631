import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    # Gemini Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD_9mYPY7gFm--DgjFV0QZYXUJ5Y7J6imY")
    
    # Google Custom Search Configuration
    GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY", "AIzaSyAz-lJLZBA-5tFZ1vWfgZew4Crc0s8yPQE")
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "a67b9550da4c04a5b")
    
    # Local Mode Configuration
    USE_LOCAL_MODE = os.environ.get("USE_LOCAL_MODE", "false").lower() == "true"
    LOCAL_LLM_MODEL = os.environ.get("LOCAL_LLM_MODEL", "llama3.2:3b")

