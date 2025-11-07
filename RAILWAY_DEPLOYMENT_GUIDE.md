# GradeMate Backend - Railway Deployment Guide

This guide will help you deploy your FastAPI backend to Railway with a MySQL database.

## 🚀 Quick Start

### Step 1: Set up Railway Account

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub (recommended)
   - Connect your GitHub account

### Step 2: Create New Project

1. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `Backend` folder as the root directory

### Step 3: Add MySQL Database

1. **Add Database Service**
   - In your Railway project dashboard
   - Click "New" → "Database" → "Add MySQL"
   - Railway will automatically provision a MySQL database

2. **Get Database Connection Details**
   - Click on your MySQL service
   - Go to the "Variables" tab
   - Copy the connection details:
     - `MYSQL_URL`
     - `MYSQL_HOST`
     - `MYSQL_PORT`
     - `MYSQL_DATABASE`
     - `MYSQL_USER`
     - `MYSQL_PASSWORD`

### Step 4: Configure Environment Variables

1. **Set Environment Variables**
   - In your Railway project dashboard
   - Click on your FastAPI service
   - Go to "Variables" tab
   - Add these variables:

   ```
   ENVIRONMENT=production
   DATABASE_URL=${{MySQL.MYSQL_URL}}
   DATABASE_HOST=${{MySQL.MYSQL_HOST}}
   DATABASE_PORT=${{MySQL.MYSQL_PORT}}
   DATABASE_NAME=${{MySQL.MYSQL_DATABASE}}
   DATABASE_USER=${{MySQL.MYSQL_USER}}
   DATABASE_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
   CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://your-custom-domain.com
   GOOGLE_API_KEY=your-google-api-key
   ```

2. **Custom Domain (Optional)**
   - Go to "Settings" → "Domains"
   - Add your custom domain
   - Update CORS_ORIGINS with your domain

### Step 5: Deploy

1. **Automatic Deployment**
   - Railway will automatically deploy when you push to your main branch
   - Check the "Deployments" tab for build logs

2. **Manual Deployment**
   - Click "Deploy" in the Railway dashboard
   - Or push changes to your connected GitHub repository

## 🔧 Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🗄️ Database Setup

### Option 1: Railway MySQL (Recommended)
- **Pros**: Integrated with Railway, automatic backups, easy scaling
- **Setup**: Add MySQL service in Railway dashboard
- **Connection**: Use Railway's automatic environment variables

### Option 2: External Database
- **PlanetScale**: `mysql+pymysql://user:pass@aws.connect.psdb.cloud/db?ssl={"rejectUnauthorized":true}`
- **Neon**: `postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/db`
- **Supabase**: `postgresql://user:pass@db.xxx.supabase.co:5432/postgres`

### Database Migration
Run the database setup script after deployment:

```bash
# SSH into your Railway service (if needed)
railway run python setup_database.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs in Railway dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **Database Connection Issues**
   - Verify environment variables are set correctly
   - Check database service is running
   - Ensure connection string format is correct

3. **CORS Issues**
   - Update `CORS_ORIGINS` with your frontend URL
   - Check environment variables in Railway dashboard

4. **File Upload Issues**
   - Railway has file size limits
   - Consider using cloud storage for larger files

### Debugging

1. **Check Railway Logs**
   - Go to your service → "Deployments" → Click on deployment
   - View build and runtime logs

2. **Test Locally with Railway Environment**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Link to your project
   railway link
   
   # Run locally with Railway environment
   railway run uvicorn app.main:app --reload
   ```

3. **Database Connection Test**
   ```bash
   railway run python -c "
   from app.config import settings
   from sqlalchemy import create_engine
   engine = create_engine(settings.database_url)
   print('Database connection successful!')
   "
   ```

## 📊 Railway Features

### Automatic Scaling
- Railway automatically scales based on traffic
- No manual configuration needed

### Built-in Monitoring
- Real-time logs
- Performance metrics
- Error tracking

### Easy Rollbacks
- One-click rollback to previous deployments
- Automatic health checks

### Custom Domains
- Add custom domains in settings
- Automatic SSL certificates

## 💰 Pricing

### Free Tier
- $5 credit per month
- 500 hours of usage
- Perfect for development and small projects

### Usage-Based Pricing
- Pay only for what you use
- Scales with your application
- No hidden fees

## 🚀 Advanced Configuration

### Custom Start Command
Update `railway.json`:
```json
{
  "deploy": {
    "startCommand": "gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
  }
}
```

### Health Checks
Railway automatically checks your `/health` endpoint:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### Environment-Specific Configs
Create different configurations for staging/production:
```json
{
  "environments": {
    "production": {
      "variables": {
        "ENVIRONMENT": "production"
      }
    },
    "staging": {
      "variables": {
        "ENVIRONMENT": "staging"
      }
    }
  }
}
```

## 📝 Next Steps

1. **Set up CI/CD**
   - Connect GitHub repository
   - Enable automatic deployments

2. **Add Monitoring**
   - Set up Railway monitoring
   - Add error tracking (Sentry)

3. **Optimize Performance**
   - Add caching
   - Optimize database queries
   - Use CDN for static assets

4. **Security**
   - Add rate limiting
   - Implement API authentication
   - Use HTTPS everywhere

## 🆘 Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: Create issues in your repository

## 🎉 Success!

Once deployed, your API will be available at:
- **Railway URL**: `https://your-app-name.up.railway.app`
- **Custom Domain**: `https://your-custom-domain.com`

Update your frontend to use the new Railway API URL!
