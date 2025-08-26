import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Model configuration
MODEL_NAME = "gpt-4o-mini"
MAX_TOKENS = 250
TEMPERATURE = 0.7

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Centralized OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Debug check (remove after testing)
if not OPENAI_API_KEY:
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
else:
    print("✅ OpenAI client initialized successfully")