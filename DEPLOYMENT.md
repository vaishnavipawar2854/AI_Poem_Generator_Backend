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

##### Error: "Preparing metadata (pyproject.toml)" / "maturin" / "cargo" failures

If you see errors mentioning `maturin`, `cargo`, or `metadata-generation-failed` during the build (often referencing `pyproject.toml`), this usually means pip attempted to build a Rust-based wheel from source (for example `pydantic-core`). On Render's build environment this can fail due to missing Rust toolchain or read-only filesystem issues.

Workarounds:

- Prefer binary wheels so pip doesn't try to build from source. Update your `render.yaml` build command to upgrade build tools and install with `--prefer-binary`:

   ```yaml
   buildCommand: >
      pip install --upgrade pip setuptools wheel
      pip install --prefer-binary --no-cache-dir -r requirements.txt
   ```

- Alternatively, pin packages to versions that have prebuilt wheels for your Python version, or add a `pyproject.toml`/`setup.py` so pip can use prebuilt metadata.

- If your dependency strictly requires building native extensions, add a pre-build step to install Rust toolchain — but this is generally discouraged on Render's free containers.

These changes are already applied in the `render.yaml` in this repository and should avoid invoking maturin/cargo during install.

##### Additional workaround: read-only Cargo cache errors

If the logs show errors like `failed to create directory '/usr/local/cargo/registry/cache...'` or `Read-only file system (os error 30)`, instruct the build to use writable temporary CARGO/RUSTUP locations. The `render.yaml` in this repo now creates `/tmp/.cargo` and `/tmp/.rustup` and sets `CARGO_HOME` and `RUSTUP_HOME` accordingly before running pip. That prevents maturin/cargo from trying to write to system-owned paths.

Example build snippet already used in this repo's `render.yaml`:

```yaml
buildCommand: >
   mkdir -p /tmp/.cargo /tmp/.rustup
   export CARGO_HOME=/tmp/.cargo
   export RUSTUP_HOME=/tmp/.rustup
   pip install --upgrade pip setuptools wheel
   pip install --prefer-binary --no-cache-dir -r requirements.txt
```

Persistent env-vars alternative

If the transient `export` approach still fails in your Render build environment, add persistent environment variables in the Render dashboard under the service's Environment section:

- `CARGO_HOME` = `/tmp/.cargo`
- `RUSTUP_HOME` = `/tmp/.rustup`

This ensures any subprocess (like `maturin` invoked by pip) uses writable cache locations and avoids attempts to write under `/usr/local/cargo` which is read-only on Render's containers.

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