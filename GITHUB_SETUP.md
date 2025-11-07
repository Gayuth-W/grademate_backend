# GitHub Setup Guide for GradeMate Backend

## ⚠️ IMPORTANT SECURITY NOTICE

**NEVER commit API keys, credentials, or sensitive data to GitHub!**

This guide will help you set up your project safely for GitHub.

## Prerequisites

1. GitHub account
2. Git installed on your machine
3. Your Google Cloud service account JSON file

## Step 1: Initialize Git Repository

```bash
cd Backend/grademateback
git init
```

## Step 2: Set Up Environment Variables

### For Local Development:

1. Copy the template file:
   ```bash
   cp env.template .env
   ```

2. Edit `.env` and add your actual credentials:
   ```bash
   # Convert your apikeys.json to a single line JSON string
   # Replace newlines with \n and escape quotes
   GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-id",...}
   ```

### For Production (Render/Heroku/etc.):

Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS_JSON` in your deployment platform with your service account JSON as a single-line string.

## Step 3: Verify .gitignore

Make sure these files are in your `.gitignore`:
- `apikeys.json`
- `.env`
- `uploads/`
- `results/`
- `__pycache__/`
- `env/`

## Step 4: Add Files to Git

```bash
git add .
git commit -m "Initial commit: GradeMate backend setup"
```

## Step 5: Create GitHub Repository

1. Go to GitHub.com
2. Click "New repository"
3. Name it (e.g., "grademate-backend")
4. **DO NOT** initialize with README (you already have files)
5. Click "Create repository"

## Step 6: Connect Local Repository to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 7: Set Up Environment Variables on GitHub (for CI/CD)

If you plan to use GitHub Actions:

1. Go to your repository on GitHub
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Add these repository secrets:
   - `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Your service account JSON as a single line
   - `DATABASE_URL`: Your database connection string
   - Any other sensitive environment variables

## Security Checklist

- [ ] `apikeys.json` is in `.gitignore`
- [ ] `.env` is in `.gitignore`
- [ ] No sensitive data in committed files
- [ ] Environment variables set up for deployment
- [ ] Repository secrets configured (if using CI/CD)

## Converting JSON to Environment Variable

To convert your `apikeys.json` to a single-line environment variable:

```python
import json

# Read your JSON file
with open('apikeys.json', 'r') as f:
    data = json.load(f)

# Convert to single line string
json_string = json.dumps(data)
print(json_string)
```

Copy the output and use it as your `GOOGLE_APPLICATION_CREDENTIALS_JSON` environment variable.

## Troubleshooting

### "No Google Cloud credentials found"
- Make sure `GOOGLE_APPLICATION_CREDENTIALS_JSON` environment variable is set
- Verify the JSON string is valid (no line breaks, proper escaping)

### "Credentials file not found"
- This is normal if you're using environment variables
- The code will fall back to environment variables automatically

## Need Help?

If you encounter issues:
1. Check that all sensitive files are in `.gitignore`
2. Verify environment variables are set correctly
3. Test locally before pushing to GitHub
4. Never commit files with actual API keys or passwords
