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

## Deployment on Render

This project is configured for deployment on [Render](https://render.com/). The `render.yaml` file contains all necessary configuration.

### Prerequisites for Deployment

1. Push your code to a GitHub repository
2. Create a Render account and connect it to your GitHub repository
3. Set up environment variables in Render dashboard

### Required Environment Variables

Set these in your Render service dashboard:

- `OPENAI_API_KEY`: Your OpenAI API key (required for poem generation)
- `FRONTEND_URL`: Your frontend application URL (for CORS configuration)
- `ENV`: Set to "production" (automatically configured in render.yaml)
- `HOST`: Set to "0.0.0.0" (automatically configured in render.yaml)
- `PORT`: Automatically provided by Render

### Deployment Steps

1. Connect your GitHub repository to Render
2. Render will automatically detect the `render.yaml` configuration
3. Set the required environment variables in the Render dashboard
4. Deploy the service

### Deployment Configuration Files

- `render.yaml`: Main Render configuration file
- `start.sh`: Production startup script (alternative)
- `requirements.txt`: Updated with production dependencies

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application
│   ├── models/           # Pydantic models
│   └── services/         # Business logic
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment configuration  
├── start.sh             # Production startup script
└── .env.example         # Environment variables template
```