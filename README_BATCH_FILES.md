# GradeMate Backend - Batch Files

This directory contains batch files to easily start and manage the GradeMate backend server.

## Available Batch Files

### 1. `start_backend.bat` (Recommended)
**Full-featured startup script with error checking and dependency management**

Features:
- ✅ Checks if Python is installed
- ✅ Activates virtual environment (if available)
- ✅ Installs/updates dependencies
- ✅ Provides clear status messages
- ✅ Shows server URLs and documentation links
- ✅ Handles errors gracefully

**Usage:**
```cmd
.\start_backend.bat
```

### 2. `quick_start.bat`
**Minimal startup script for quick testing**

Features:
- ⚡ Fast startup
- 🎯 Direct server launch
- 📝 Minimal output

**Usage:**
```cmd
.\quick_start.bat
```

### 3. `stop_backend.bat`
**Stops any running backend processes**

Features:
- 🛑 Kills Python processes running uvicorn
- 🔍 Finds processes using port 8000
- 🧹 Cleans up running servers

**Usage:**
```cmd
.\stop_backend.bat
```

## Server Information

Once started, the backend server will be available at:

- **Main Server**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## Troubleshooting

### Common Issues:

1. **"Python not found"**
   - Install Python 3.8+ from https://python.org
   - Make sure Python is added to your system PATH

2. **"Module not found"**
   - Run `pip install -r requirements.txt` manually
   - Check if virtual environment is activated

3. **"Port 8000 already in use"**
   - Run `.\stop_backend.bat` to stop existing servers
   - Or change the port in the batch file

4. **Database connection errors**
   - Check your `config.py` database settings
   - Ensure MySQL server is running
   - Verify database credentials

### Manual Commands:

If batch files don't work, you can run these commands manually:

```cmd
# Activate virtual environment (if exists)
env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Development Tips

- Use `start_backend.bat` for development (includes auto-reload)
- The server will automatically restart when you make code changes
- Check the console output for any error messages
- Use `stop_backend.bat` if the server becomes unresponsive

## API Endpoints

The backend provides these main endpoints:

- `POST /api/marking-schemes/upload` - Upload marking scheme PDFs
- `POST /api/answer-sheets/upload` - Upload answer sheets
- `POST /api/grading/grade` - Start grading process
- `GET /api/grading/results` - Get grading results
- `GET /api/statistics` - Get system statistics

For full API documentation, visit: http://127.0.0.1:8000/docs
