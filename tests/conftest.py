import os

# Define variaveis de ambiente minimas para os testes rodarem
# sem precisar de um .env real
os.environ.setdefault("GROQ_API_KEY", "test_key")
os.environ.setdefault("NEXUS_DISABLE_GRADIO", "true")
os.environ.setdefault("LOG_FORMAT", "text")
os.environ.setdefault("LOG_LEVEL", "WARNING")
