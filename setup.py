#!/usr/bin/env python3
"""
Setup script for AI Poem Generator Backend
"""

from setuptools import setup, find_packages

setup(
    name="ai-poem-generator-backend",
    version="1.0.0",
    description="AI Poem Generator Backend API built with FastAPI",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "openai>=1.3.7",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "slowapi>=0.1.9",
        "httpx>=0.25.2",
        "typing-extensions>=4.5.0",
    ],
)