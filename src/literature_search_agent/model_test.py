from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider

class CityLocation(BaseModel):
    city: str
    country: str

ollama_model = OpenAIChatModel(
    model_name="koesn/llama3-openbiollm-8b",
    provider=OllamaProvider(base_url="http://localhost:11434/v1"),
    temperature=0.3,  # Lower = more deterministic (0-2, default 1.0)
    top_p=0.9,        # Nucleus sampling (0-1)
    top_k=40,         # Keep top K tokens (default None)
    max_tokens=1024,  # Max response length
)

agent = Agent(ollama_model, output_type=CityLocation)

result = agent.run_sync("Where were the olympics held in 2012?")
print(result.output)
print(result.usage())