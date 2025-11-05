from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from supabase import create_client
import requests
import PyPDF2
from docx import Document
import io
import os
from datetime import datetime
from dotenv import load_dotenv
from bson import ObjectId

# Load .env
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Resume Parser API")

# Environment variables
MONGODB_URL = os.getenv("MONGODB_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL is not set in environment")

# Database clients
mongo_client = AsyncIOMotorClient(MONGODB_URL)
db = mongo_client.resume_parser
candidates_collection = db.candidates

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pydantic models
class QARequest(BaseModel):
    question: str


# Helper functions - FIXED VERSION
def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or DOCX - takes BYTES not filepath"""
    name = filename.lower()
    
    try:
        if name.endswith(".pdf"):
            # file_bytes is already bytes, wrap it in BytesIO
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts)
            
        elif name.endswith(".docx"):
            # file_bytes is already bytes, wrap it in BytesIO
            doc = Document(io.BytesIO(file_bytes))
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
    
    return ""


def parse_resume_simple(text: str) -> dict:
    """Simple resume parsing using keywords"""
    import re

    lower_text = text.lower()

    # Extract skills
    skill_keywords = [
        "python", "java", "javascript", "react", "node", "django",
        "flask", "fastapi", "mongodb", "sql", "aws", "docker", "git",
        "kubernetes", "typescript", "postgresql", "mysql", "redis"
    ]
    skills = [skill for skill in skill_keywords if skill in lower_text]

    # Extract education
    degrees = re.findall(r'\b(B\.?Tech|M\.?Tech|Bachelor|Master|MBA|Ph\.?D|BSc|MSc)\b', text, re.I)

    # Extract years
    years = re.findall(r'\b(?:19|20)\d{2}\b', text)

    # Extract companies
    companies = re.findall(r'\bat\s+([A-Z][A-Za-z0-9&\.\- ]{1,60})', text)

    # Extract certifications
    certs = re.findall(r'\b(AWS|Azure|Google Cloud|Certified|CCNA|PMP)\b', text, re.I)

    # Simple intro
    intro = ' '.join(text.split()[:30])

    return {
        "education": {
            "degrees": list(dict.fromkeys([d.strip() for d in degrees]))[:2],
            "graduation_year": years[-1] if years else ""
        },
        "experience": {
            "companies": list(dict.fromkeys([c.strip() for c in companies]))[:3],
            "total_years": 0
        },
        "skills": list(dict.fromkeys(skills))[:15],
        "hobbies": [],
        "certifications": list(dict.fromkeys([c.strip() for c in certs])),
        "projects": [],
        "introduction": intro
    }


# API Endpoints
@app.get("/")
def home():
    return {"message": "Resume Parser API is running"}


@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and process resume"""
    filename = file.filename or ""
    lower = filename.lower()
    
    if not (lower.endswith(".pdf") or lower.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files allowed")

    try:
        # Read file as bytes
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Upload to Supabase
        file_path = f"{int(datetime.utcnow().timestamp())}_{filename}"
        
        try:
            bucket = supabase.storage.from_("resumes")
            bucket.upload(file_path, io.BytesIO(content))
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/resumes/{file_path}"
        except Exception as e:
            print(f"Supabase error: {e}")
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/resumes/{file_path}"

        metadata = {
            "id": file_path,
            "filename": filename,
            "created_at": datetime.utcnow().isoformat(),
            "public_url": file_url
        }

        # Extract text from bytes (NOT from filepath)
        text = extract_text_from_file(content, filename)
        
        if not text:
            text = "Unable to extract text - stored for later processing"

        # Parse resume
        parsed = parse_resume_simple(text)

        # Store in MongoDB
        candidate_doc = {
            "candidate_id": metadata["id"],
            **parsed,
            "full_text": text[:5000],  # Limit size
            "filename": filename,
            "upload_date": metadata["created_at"]
        }

        result = await candidates_collection.insert_one(candidate_doc)

        return {
            "message": "Resume uploaded successfully",
            "candidate_id": str(result.inserted_id),
            "supabase_id": metadata["id"],
            "public_url": metadata["public_url"],
            "skills_extracted": len(parsed.get("skills", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/candidates")
async def get_candidates():
    """List all candidates"""
    try:
        candidates = await candidates_collection.find().to_list(length=100)

        result = []
        for c in candidates:
            result.append({
                "id": str(c.get("_id")),
                "candidate_id": c.get("candidate_id", ""),
                "filename": c.get("filename", ""),
                "upload_date": c.get("upload_date", ""),
                "skills_count": len(c.get("skills", [])) if isinstance(c.get("skills", []), list) else 0,
                "education": c.get("education", {}).get("degrees", [])
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Get single candidate details"""
    try:
        candidate = None
        
        # Try ObjectId first
        try:
            candidate = await candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        except:
            # Try candidate_id field
            candidate = await candidates_collection.find_one({"candidate_id": candidate_id})

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        candidate["_id"] = str(candidate["_id"])
        return candidate

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/ask/{candidate_id}")
async def ask_question(candidate_id: str, request: QARequest):
    """Ask question about candidate"""
    try:
        candidate = None
        
        # Try ObjectId first
        try:
            candidate = await candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        except:
            # Try candidate_id field
            candidate = await candidates_collection.find_one({"candidate_id": candidate_id})

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Prepare context
        context = (
            f"Education: {candidate.get('education', {})}\n"
            f"Experience: {candidate.get('experience', {})}\n"
            f"Skills: {', '.join(candidate.get('skills', []))}\n"
            f"Certifications: {', '.join(candidate.get('certifications', []))}\n"
            f"Text: {candidate.get('full_text', '')[:2000]}"
        )

        answer = ""
        confidence = 0.5

        # Try Hugging Face API
        if HF_TOKEN:
            try:
                API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {
                    "inputs": {
                        "question": request.question,
                        "context": context
                    }
                }

                response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and "answer" in result:
                        answer = result.get("answer", "")
                        confidence = 0.85
                    elif isinstance(result, list) and len(result) > 0:
                        answer = result[0].get("answer", "")
                        confidence = 0.85
            except Exception as e:
                print(f"HF API error: {e}")
                answer = ""

        # Fallback if no answer from API
        if not answer:
            q_lower = request.question.lower()
            if "graduation" in q_lower or "year" in q_lower:
                year = candidate.get("education", {}).get("graduation_year", "")
                answer = f"Graduation year: {year}" if year else "Not found in resume"
            elif "skill" in q_lower:
                skills = candidate.get("skills", [])
                answer = f"Skills: {', '.join(skills)}" if skills else "No skills found"
            else:
                answer = "Could not find answer in resume data"
            confidence = 0.5

        return {
            "candidate_id": candidate_id,
            "question": request.question,
            "answer": answer,
            "confidence": confidence
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
