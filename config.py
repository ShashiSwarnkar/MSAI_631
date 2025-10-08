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
    
