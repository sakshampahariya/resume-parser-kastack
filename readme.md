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

## Interactive API Documentation

Visit \`http://localhost:8000/docs\` to see and test all endpoints with Swagger UI.

## Environment Variables

| Variable | Description |
|----------|-------------|
| \`MONGODB_URL\` | MongoDB connection string with credentials |
| \`SUPABASE_URL\` | Supabase project URL |
| \`SUPABASE_KEY\` | Supabase anonymous key |
| \`HUGGINGFACE_TOKEN\` | Hugging Face API token for ML models |

## How It Works

1. **Upload Resume** - User uploads PDF/DOCX file via \`/upload\` endpoint
2. **Extract Text** - PyPDF2/python-docx extracts text from file
3. **Parse Resume** - Uses keyword matching to extract education, skills, experience
4. **Store Data** - Saves candidate info in MongoDB + file in Supabase
5. **Answer Questions** - Uses Hugging Face QA model to answer questions about candidate

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

