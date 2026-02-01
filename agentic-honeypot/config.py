"""
Configuration settings for agentic-honeypot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Detection Configuration
SCAM_CONFIDENCE_THRESHOLD = float(os.getenv("SCAM_CONFIDENCE_THRESHOLD", 0.7))

# Agent Configuration
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4")
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 30))

# Storage Configuration
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "memory")  # memory, redis, db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./honeypot.db")

# GUVI Callback Configuration
GUVI_ENDPOINT = os.getenv("GUVI_ENDPOINT", "https://guvi.example.com/api/v1/intelligence")
GUVI_API_KEY = os.getenv("GUVI_API_KEY", "your-guvi-api-key-here")
GUVI_TIMEOUT = int(os.getenv("GUVI_TIMEOUT", 10))
GUVI_RETRY_COUNT = int(os.getenv("GUVI_RETRY_COUNT", 3))
GUVI_RETRY_DELAY = int(os.getenv("GUVI_RETRY_DELAY", 5))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "honeypot.log")
