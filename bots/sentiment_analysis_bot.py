    # Copyright (c) Microsoft Corporation. All rights reserved.
    # Licensed under the MIT License.

    from botbuilder.core import ActivityHandler, TurnContext
    from botbuilder.schema import ChannelAccount
    
    # Import the Azure SDK clients
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient
    
    from config import DefaultConfig
    
    class SentimentBot(ActivityHandler):
        def __init__(self, config: DefaultConfig):
            self.config = config
            # Create the client for the Azure Language Service
            self.text_analytics_client = self._create_text_analytics_client()

        def _create_text_analytics_client(self) -> TextAnalyticsClient:
            """Creates and authenticates the client to connect to Azure."""
            if not self.config.LANGUAGE_API_ENDPOINT or not self.config.LANGUAGE_API_KEY:
                raise ValueError("Azure Language Service endpoint and key must be configured.")
            
            credential = AzureKeyCredential(self.config.LANGUAGE_API_KEY)
            client = TextAnalyticsClient(endpoint=self.config.LANGUAGE_API_ENDPOINT, credential=credential)
            return client

        async def on_members_added_activity(
            self, members_added: ChannelAccount, turn_context: TurnContext
        ):
            for member_added in members_added:
                if member_added.id != turn_context.activity.recipient.id:
                    await turn_context.send_activity(
                        "Hello! I am the Sentiment Bot. Send me a message, and I'll tell you the sentiment."
                    )
    
        async def on_message_activity(self, turn_context: TurnContext):
            user_text = turn_context.activity.text
            response_text = ""
    
            try:
                # Call the Azure AI service
                documents = [user_text]
                result = self.text_analytics_client.analyze_sentiment(documents, show_opinion_mining=True)
                docs = [doc for doc in result if not doc.is_error]
    
                # Process the response from the service
                if docs:
                    doc = docs[0]
                    sentiment = doc.sentiment
                    pos_score = doc.confidence_scores.positive
                    neg_score = doc.confidence_scores.negative
    
                    # Create a user-friendly response
                    response_text = f"The sentiment of your message is **{sentiment}**.\n\n"
                    response_text += f"* Positive score: {pos_score:.2f}\n"
                    response_text += f"* Negative score: {neg_score:.2f}"
                else:
                    response_text = "Sorry, I couldn't analyze the sentiment for that message."
    
            except Exception as e:
                print(f"Error calling Azure AI Service: {e}")
                response_text = "Sorry, I ran into an issue while trying to connect to the AI service."
    
            await turn_context.send_activity(response_text)
    
