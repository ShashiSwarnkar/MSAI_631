"""
Local LLM Interface using Ollama
Provides the same interface as Gemini API but runs locally
"""
import requests
import json

class LocalLLM:
    def __init__(self, model="llama3.2:3b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt, temperature=0.7, max_tokens=1000):
        """Generate response using local Ollama model."""
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.ConnectionError:
            print(f"Error: Cannot connect to Ollama. Make sure it's running: 'ollama serve'")
            return None
        except Exception as e:
            print(f"Local LLM Error: {e}")
            return None
    
    def extract_json(self, prompt):
        """Extract JSON from LLM response."""
        response = self.generate(prompt, temperature=0.3)
        if response:
            # Clean up response to extract JSON
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            return response.strip()
        return None
    
    def test_connection(self):
        """Test if Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if self.model in model_names:
                print(f"✓ Ollama is running and {self.model} is available")
                return True
            else:
                print(f"✗ Model {self.model} not found. Available models: {model_names}")
                print(f"  Download with: ollama pull {self.model}")
                return False
        except:
            print("✗ Ollama is not running. Start it with: ollama serve")
            return False
