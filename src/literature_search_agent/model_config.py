# config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class ModelConfig(BaseSettings):
    """Configuration for all test models"""
    
    # Ollama connection
    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Ollama API base URL"
    )
    
    # Model names - update these to match your 'ollama list' output
    models: dict = {
        "llama3": {
            "name": "llama3:8b",
            "description": "Llama 3 8B Instruct (8-bit)"
        },
        "qwen": {
            "name": "qwen2.5:7b-instruct-q8_0",
            "description": "Qwen 2.5 7B Instruct (8-bit)"
        },
        "biomistral": {
            "name": "jsk/bio-mistral:latest",
            "description": "BioMistral 7B"
        },
        "openbiollm": {
            "name": "koesn/llama3-openbiollm-8b",
            "description": "Llama3 OpenBioLLM 8B"
        }
    }
    
    # Inference parameters
    temperature: float = Field(default=0.3, description="Model temperature (0-1)")
    max_tokens: int = Field(default=500, description="Max response length")
    top_p: float = Field(default=0.9, description="Nucleus sampling")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = ModelConfig()