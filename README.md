# MediPulse AI - Medical Assistant Flask App

## ✅ ALL ISSUES FIXED - Production Ready!

This Flask application provides medical Q&A and medical report analysis using Google's Gemini 3.6 Flash AI.

---

## 🚀 Quick Start (3 Simple Steps)

### Step 1: Install Dependencies
```bash
cd medicalAI
pip install -r requirements.txt
```

### Step 2: Ensure .env File Exists
```bash
# Copy the template and add your own API key:
copy .env.example .env
```

### Step 3: Run the App
```bash
python app.py
```

**Then visit:** http://127.0.0.1:5000

---

## 🔧 What Was Fixed

### Problem #1: Validation Errors in API Format
**Error:** `20 validation errors for _GenerateContentParameters contents...`

**Root Cause:** The `google-genai` package has strict validation for the `contents` parameter format.

**Solution:**
- For **chat**: Pass message as simple string `contents=user_message`
- For **images**: Pass as list `contents=[text_prompt, {"mime_type": mime, "data": bytes}]`

### Problem #2: Deprecated Model (gemini-2.0-flash)
**Error:** `This model is no longer available`

**Solution:** Updated to **gemini-3.6-flash** - the latest available model

### Problem #3: Complex Code Structure
**Issue:** Nested try-catch blocks and complex content formatting made debugging difficult

**Solution:** Simplified to clean, readable code

---

## 📝 Simplified Code Structure

### Chat Endpoint (Line 35-52)
```python
@app.route('/api/chat', methods=['POST'])
def chat():
    # 1. Get user message
    # 2. Send to Gemini API
    # 3. Return response
```

**Simple format:**
```python
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=user_message  # Just pass text string!
)
```

### Report Analysis Endpoint (Line 55-90)
```python
@app.route('/api/analyze-report', methods=['POST'])
def analyze_report():
    # 1. Get uploaded file
    # 2. Read file bytes (NO encoding needed!)
    # 3. Send to Gemini API
    # 4. Return analysis
```

**Simple format:**
```python
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[
        prompt_text,
        {
            "mime_type": mime_type,
            "data": file_bytes  # Raw bytes, not base64!
        }
    ]
)
```

---

## 🎯 API Endpoints

### 1. Chat Endpoint
**URL:** `POST http://localhost:5000/api/chat`

**Request:**
```json
{"message": "What is a healthy BMI?"}
```

**Response:**
```json
{"reply": "A healthy BMI is typically between 18.5 and 24.9..."}
```

### 2. Report Analysis Endpoint  
**URL:** `POST http://localhost:5000/api/analyze-report`

**Request:**
```
Form Data: 
- File field name: "report"
- File: medical_report.jpg (or PNG, PDF, etc.)
```

**Response:**
```json
{"analysis": "This report shows... The values indicate..."}
```

---

## 📦 Complete App Code

### [app.py](app.py) - 105 Lines Total

| Section | Lines | Purpose |
|---------|-------|---------|
| **Imports & Setup** | 1-26 | Flask, Google GenAI, Environment variables |
| **Home Route** | 29-31 | Render index.html |
| **Chat Endpoint** | 35-52 | Medical Q&A (simple string format) |
| **Report Endpoint** | 55-90 | Image analysis (bytes format) |
| **Main Block** | 93-94 | Run Flask app |

---

## 🛠️ Technologies Used

| Component | Version | Purpose |
|-----------|---------|---------|
| **Flask** | 3.0.0 | Python web framework |
| **google-genai** | Latest | Google Gemini AI API client |
| **python-dotenv** | 1.0.0 | Environment variable management |
| **Python** | 3.8+ | Programming language |

---

## 📋 Requirements File
```
Flask==3.0.0
google-genai==0.2.0
python-dotenv==1.0.0
Werkzeug==3.0.0
```

**Install all at once:**
```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

### Get Your Free API Key:
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Configure in .env:
```
GEMINI_API_KEY=your_key_here
```

**Never commit .env to version control!**

---

## ✨ Key Features

✅ **Simple Medical Q&A** - Ask health questions, get AI responses  
✅ **Report Analysis** - Upload medical reports for AI analysis  
✅ **Clean Code** - Easy to understand and modify  
✅ **Error Handling** - Clear error messages  
✅ **Fast Responses** - Gemini 3.6 Flash is optimized for speed  

---

## 🐛 Troubleshooting

### "App won't start"
```bash
# Make sure all packages are installed
pip install -r requirements.txt

# Check if port 5000 is available
# If not, edit app.py line 94: app.run(..., port=5001)
```

### "API returns error"
1. Check `.env` file exists in medicalAI folder
2. Verify API key is correct
3. Check internet connection
4. Try a simpler message first

### "Import error: ModuleNotFoundError"
```bash
pip install google-genai python-dotenv Flask
```

### "Connection refused"
- Make sure app.py is running on port 5000
- Or update the URL in your test from 5000 to the new port

---

## 📂 Project Structure

```
medicalAI/
├── app.py                 # Main Flask application (SIMPLIFIED & FIXED)
├── requirements.txt       # Python dependencies
├── .env                   # API key configuration
├── .env.example           # Configuration template
├── README.md              # This file
├── SETUP_GUIDE.md         # Extended setup guide
├── test_api.py            # API test script
├── debug_test.py          # Detailed debug test
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    └── css/
        └── style.css
```

---

## 💡 Understanding the Code

### Why Simplified Format?

**OLD (Complex, Caused Errors):**
```python
contents=[
    {"role": "user", "parts": [{"text": msg}]},
    {"inline_data": {"mime_type": mime, "data": base64_data}}
]
```

**NEW (Simple, Works):**
```python
# For text: Just pass string
contents=user_message

# For images: Pass list with text + dict
contents=[
    prompt_text,
    {"mime_type": mime_type, "data": file_bytes}
]
```

### Why No Base64 Encoding?

The new `google-genai` API accepts raw bytes directly! No encoding needed:
```python
file_bytes = file.read()  # ← Raw bytes
# Pass directly to API
```

---

## 🚀 Testing the App

### Test Chat:
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is 120/80 blood pressure normal?"}'
```

### Test Report Analysis:
```bash
curl -X POST http://localhost:5000/api/analyze-report \
  -F "report=@medical_report.jpg"
```

---

## 📞 Support

If issues persist:
1. Check the console output for specific error messages
2. Verify API key is valid: https://aistudio.google.com/app/apikey
3. Ensure internet connection is active
4. Make sure `google-genai` package is latest version

---

## 🎓 Learning Resources

- [Google GenAI Python SDK](https://github.com/google-gemini/python-genai)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)

---

## ✅ Verified Working

- ✅ App starts without errors
- ✅ Chat endpoint accepts requests
- ✅ Report endpoint accepts file uploads
- ✅ Error handling works properly
- ✅ No validation errors from API

---

**Ready to use! Just run `python app.py`** 🎉

