# 🎭 AI Poem Generator - Backend

A powerful FastAPI backend for generating beautiful poems using OpenAI's GPT models.

## 🚀 Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/vaishnavipawar2854/AI_Poem_Generator_Backend.git
   cd AI_Poem_Generator_Backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv poem_env
   poem_env\Scripts\activate  # On Windows
   # source poem_env/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env file and add your OPENAI_API_KEY
   ```

5. Run the server:
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application
│   ├── models/           # Pydantic models
│   └── services/         # Business logic
├── tests/                # Test files
├── requirements.txt      # Python dependencies
└── .env.example         # Environment variables template
```