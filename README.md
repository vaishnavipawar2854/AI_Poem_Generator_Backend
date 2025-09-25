# AI Poem Generator - Backend

This is the FastAPI backend for the AI Poem Generator application.

## Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv poem_env
   poem_env\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your OpenAI API key.

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