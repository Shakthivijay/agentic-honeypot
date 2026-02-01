#!/usr/bin/env python
"""
Wrapper script to run uvicorn from correct directory
"""
import os
import sys
import uvicorn

# Change to the correct directory
os.chdir(r'c:\Users\SHAKTHI\Desktop\agentic-honeypot\agentic-honeypot')

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
