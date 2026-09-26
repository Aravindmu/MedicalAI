# MediPulse AI - Setup & Troubleshooting Guide

## ✅ All Issues Fixed!

### Problems Solved:
1. ✅ **Deprecated Package Warning**: Migrated from `google.generativeai` to `google-genai` (new modern package)
2. ✅ **ModuleNotFoundError**: Installed `python-dotenv` package
3. ✅ **Gemini API 404 Errors**: Updated to use stable `gemini-2.0-flash` with automatic fallback support
4. ✅ **Missing Dependencies**: Added all required packages to `requirements.txt`
5. ✅ **API Key Security**: Implemented environment variable configuration with `.env` file

### Quick Start:

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Create `.env` File
The `.env` file has been created with your API key. If you need to change it:
```
GEMINI_API_KEY=your_api_key_here
```

#### Step 3: Run the App
```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000`

---

## Detailed Changes

### 1. Package Migration
**OLD (Deprecated):**
```python
import google.generativeai as genai
```

**NEW (Modern):**
```python
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)
```

### 2. API Configuration
**OLD:**
```python
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash", ...)
```

**NEW:**
```python
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=user_message,
    config={...}
)
```

### 3. Error Handling
- ✅ Better error messages with console logging
- ✅ Automatic fallback from `gemini-2.0-flash` to `gemini-1.5-flash`
- ✅ Detailed error responses for debugging

### 4. Dependencies
**Updated `requirements.txt`:**
```
Flask==3.0.0
google-genai==0.1.0
python-dotenv==1.0.0
Werkzeug==3.0.0
```

---

## Environment Configuration

### Setup `.env` File
Create a `.env` file in the medicalAI directory:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Then edit `.env` and add your API key:
```
GEMINI_API_KEY=your_api_key_here
```

⚠️ **IMPORTANT**: Never commit `.env` to version control! It contains sensitive information.

---

## Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key and paste it into `.env`

---

## Testing the API

### Test Chat Endpoint
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a healthy BMI?"}'
```

### Test Report Analysis
```bash
curl -X POST http://localhost:5000/api/analyze-report \
  -F "report=@your_medical_report.pdf"
```

---

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'dotenv'
**Solution:**
```bash
pip install python-dotenv
```

### Issue: Deprecation warning about google.generativeai
**Status:** ✅ FIXED - Now using modern `google-genai` package

### Issue: API returns 404 for models/gemini-1.5-flash
**Status:** ✅ FIXED - Using `gemini-2.0-flash` with fallback support

### Issue: GEMINI_API_KEY not set
**Solution:**
- Ensure `.env` file exists in the medicalAI directory
- Check API key is correct and not expired
- Regenerate key from Google AI Studio if needed

### Issue: "API call fails with 403"
**Solution:**
- Verify API key is valid
- Ensure Generative AI API is enabled in Google Cloud Console
- Regenerate key from Google AI Studio

---

## System Requirements
- Python 3.8+
- Flask 3.0+
- google-genai package (new modern version)
- python-dotenv for environment variables

---

## Files in This Project
```
medicalAI/
├── app.py                 # Main Flask application (UPDATED)
├── requirements.txt       # Python dependencies (UPDATED)
├── .env                   # API key configuration (CREATED)
├── .env.example           # Configuration template
├── SETUP_GUIDE.md         # This file
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    └── css/
        └── style.css
```

---

## Support & Resources
- [Google Generative AI Documentation](https://ai.google.dev/docs)
- [New google-genai Package](https://github.com/google-gemini/python-genai)
- [Deprecated Package Info](https://github.com/google-gemini/deprecated-generative-ai-python)
- [Google AI Studio](https://aistudio.google.com)

