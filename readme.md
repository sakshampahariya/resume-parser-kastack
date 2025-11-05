cat <<EOF > README.md
# Resume Parser API

A FastAPI-based Resume Parser that extracts information from resumes (PDF/DOCX) using AI models, stores data in MongoDB, and provides intelligent Q&A capabilities powered by Hugging Face.

## Features

- ✅ **Resume Upload** - Upload and parse PDF/DOCX resumes
- ✅ **Text Extraction** - Automatic text extraction from resume files
- ✅ **Smart Parsing** - Extract skills, education, experience, certifications
- ✅ **Cloud Storage** - Store resume files in Supabase
- ✅ **Database** - MongoDB for candidate data storage
- ✅ **AI Q&A** - Ask questions about candidates using Hugging Face models
- ✅ **Interactive API Docs** - Swagger UI for easy testing

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Database**: MongoDB with Motor (async driver)
- **Storage**: Supabase
- **ML Models**: Hugging Face (NER for parsing, QA for questions)
- **File Processing**: PyPDF2, python-docx

## Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Supabase account
- Hugging Face API token

### Setup

1. **Clone the repository**
\`\`\`bash
git clone https://github.com/sakshampahariya/resume-parser-kastack.git
cd resume-parser-kastack
\`\`\`

2. **Create virtual environment**
\`\`\`bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
\`\`\`

3. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Create .env file**
\`\`\`
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
\`\`\`

5. **Run the application**
\`\`\`bash
python main.py
\`\`\`

The API will be available at: \`http://localhost:8000\`

## API Endpoints

### 1. GET \`/\`
Check if API is running
\`\`\`bash
curl http://localhost:8000/
\`\`\`
**Response:**
\`\`\`json
{"message": "Resume Parser API is running"}
\`\`\`

### 2. POST \`/upload\`
Upload and process a resume
\`\`\`bash
curl -X POST "http://localhost:8000/upload" \\
  -F "file=@resume.pdf"
\`\`\`
**Response:**
\`\`\`json
{
  "message": "Resume uploaded successfully",
  "candidate_id": "673a1234567890abcdef1234",
  "supabase_id": "1730784567.123_resume.pdf",
  "public_url": "https://...",
  "skills_extracted": 5
}
\`\`\`

### 3. GET \`/candidates\`
List all uploaded candidates
\`\`\`bash
curl http://localhost:8000/candidates
\`\`\`
**Response:**
\`\`\`json
[
  {
    "id": "673a1234567890abcdef1234",
    "candidate_id": "1730784567.123_resume.pdf",
    "filename": "resume.pdf",
    "upload_date": "2025-11-05T11:05:00",
    "skills_count": 12,
    "education": ["B.Tech"]
  }
]
\`\`\`

### 4. GET \`/candidate/{candidate_id}\`
Get details of a specific candidate
\`\`\`bash
curl http://localhost:8000/candidate/673a1234567890abcdef1234
\`\`\`
**Response:**
\`\`\`json
{
  "_id": "673a1234567890abcdef1234",
  "education": {
    "degrees": ["B.Tech"],
    "graduation_year": "2025"
  },
  "experience": {
    "companies": ["TCS", "Infosys"],
    "total_years": 0
  },
  "skills": ["python", "java", "django", "mongodb"],
  "certifications": ["AWS"],
  "full_text": "..."
}
\`\`\`

### 5. POST \`/ask/{candidate_id}\`
Ask a question about a candidate
\`\`\`bash
curl -X POST "http://localhost:8000/ask/673a1234567890abcdef1234" \\
  -H "Content-Type: application/json" \\
  -d '{"question": "What skills does this candidate have?"}'
\`\`\`
**Response:**
\`\`\`json
{
  "candidate_id": "673a1234567890abcdef1234",
  "question": "What skills does this candidate have?",
  "answer": "Python, Java, Django, MongoDB, AWS",
  "confidence": 0.85
}
\`\`\`

## Interactive API Documentation

Visit \`http://localhost:8000/docs\` to see and test all endpoints with Swagger UI.

## Environment Variables

| Variable | Description |
|----------|-------------|
| \`MONGODB_URL\` | MongoDB connection string with credentials |
| \`SUPABASE_URL\` | Supabase project URL |
| \`SUPABASE_KEY\` | Supabase anonymous key |
| \`HUGGINGFACE_TOKEN\` | Hugging Face API token for ML models |

## Project Structure

\`\`\`
resume-parser-kastack/
├── main.py                 # FastAPI application with all endpoints
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
└── .env                   # Environment variables (NOT in git)
\`\`\`

## Requirements

\`\`\`
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
motor==3.6.0
pymongo==4.10.1
supabase==2.9.0
python-dotenv==1.0.0
PyPDF2==3.0.1
python-docx==1.1.0
requests==2.31.0
pydantic==2.5.3
\`\`\`

## How It Works

1. **Upload Resume** - User uploads PDF/DOCX file via \`/upload\` endpoint
2. **Extract Text** - PyPDF2/python-docx extracts text from file
3. **Parse Resume** - Uses keyword matching to extract education, skills, experience
4. **Store Data** - Saves candidate info in MongoDB + file in Supabase
5. **Answer Questions** - Uses Hugging Face QA model to answer questions about candidate

## Troubleshooting

### MongoDB Connection Error
\`\`\`
pymongo.errors.InvalidURI: Username and password must be escaped
\`\`\`
**Solution:** URL-encode special characters in password using \`urllib.parse.quote_plus()\`

### Supabase Upload Error
\`\`\`
Storage bucket not found
\`\`\`
**Solution:** Create a bucket named \`resumes\` in Supabase and set it to **Public**

### Hugging Face API Timeout
\`\`\`
requests.exceptions.ConnectTimeout
\`\`\`
**Solution:** The app has fallback answers. If timeout occurs, basic keyword matching is used.

## Testing

1. Start the server: \`python main.py\`
2. Open \`http://localhost:8000/docs\`
3. Test each endpoint:
   - Upload a sample resume PDF
   - List all candidates
   - Get candidate details
   - Ask a question

## Created For

KaStack Internship Task - Resume Parser API

## Author

**Saksham Pahariya**
- MITS Gwalior, IT/Computer Science
- GitHub: https://github.com/sakshampahariya

## License

MIT License - Open to use for learning and development purposes

---

**Last Updated:** November 5, 2025

EOF
