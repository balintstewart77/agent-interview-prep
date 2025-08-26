import os
from dotenv import load_dotenv

load_dotenv()

# Model configuration
MODEL_NAME = "gpt-4o-mini"
MAX_TOKENS = 500
TEMPERATURE = 0.7

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")