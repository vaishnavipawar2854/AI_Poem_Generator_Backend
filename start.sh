#!/usr/bin/env bash
# Render start script for AI Poem Generator Backend

# Set environment variables with defaults
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export ENV=${ENV:-production}

echo "🚀 Starting AI Poem Generator API on $HOST:$PORT"
echo "📚 Environment: $ENV"

# Start the application using uvicorn
exec uvicorn app.main:app --host $HOST --port $PORT --log-level info