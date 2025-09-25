# Render Deployment Guide

## Quick Deploy to Render

This guide will help you deploy your AI Poem Generator Backend to Render.

### Step 1: Prepare Your Repository

1. Make sure all your code is committed and pushed to GitHub
2. Ensure the following files are in your repository root:
   - `render.yaml` (main configuration)
   - `requirements.txt` (with all dependencies)
   - `start.sh` (production startup script)

### Step 2: Create Render Account

1. Go to [render.com](https://render.com/)
2. Sign up or log in
3. Connect your GitHub account

### Step 3: Create New Web Service

1. Click "New" → "Web Service"
2. Select your GitHub repository
3. Configure the service:
   - **Name**: `ai-poem-generator-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Set Environment Variables

In the Render dashboard, add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `OPENAI_API_KEY` | Your OpenAI API key | **Required** - Get from OpenAI dashboard |
| `FRONTEND_URL` | Your frontend URL | Update when you deploy frontend |
| `ENV` | `production` | Already set in render.yaml |
| `HOST` | `0.0.0.0` | Already set in render.yaml |

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the build logs for any issues

### Step 6: Verify Deployment

Once deployed, test these endpoints:

- **Health Check**: `https://your-app.onrender.com/health`
- **API Docs**: `https://your-app.onrender.com/docs`
- **Root**: `https://your-app.onrender.com/`

### Expected Build Process

```bash
# Render will run these commands:
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Troubleshooting

#### Build Fails
- Check that all dependencies are in `requirements.txt`
- Ensure Python version compatibility
- Review build logs for specific errors

#### Service Won't Start
- Verify `OPENAI_API_KEY` is set correctly
- Check that the start command matches your app structure
- Review application logs in Render dashboard

#### CORS Issues
- Update `FRONTEND_URL` environment variable
- Ensure frontend domain is correct

### Free Tier Limitations

Render's free tier includes:
- 750 hours/month of runtime
- Service sleeps after 15 minutes of inactivity
- Cold start delays (up to 30 seconds)

### Production Considerations

For production deployments:
- Upgrade to a paid plan for better performance
- Set up custom domain
- Configure monitoring and alerts
- Set up database if needed
- Enable SSL (automatic on Render)

### Environment Variables Reference

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional but recommended
FRONTEND_URL=https://your-frontend-domain.onrender.com
ENV=production
HOST=0.0.0.0
```

### Support

If you encounter issues:
1. Check Render's [documentation](https://render.com/docs)
2. Review application logs in Render dashboard
3. Verify environment variables are set correctly
4. Test locally before deploying