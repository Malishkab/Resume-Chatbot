from fastapi import FastAPI
from pypdf import PdfReader
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import os
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")   

#client
client=Groq(api_key=my_api_key)
#model
model="openai/gpt-oss-120b"

#application banana hai using fast api/brodge
app=FastAPI()
#@app.get("/") #what does this mean??
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#jab lets say hum youtube.com pe click karte hai we are directed to home page, fi agr koi youtube.com/jelly pe jaye toh that means uss
#channel ka homepage pe we go so how do we decide ki hamare application ka first page ya kya dikhna chahiye? in above we used "/"  this means 
#application ke home page pe jao, below we will make someting for now that leads to ki homepage pe kya hona chahiye
#hum later kafi changes isi code me karenge to make proper backend and frontend

#read resume
def resume_parser(file_path:Path):
    res=PdfReader(file_path)
    text=""
    for pages in res.pages:
        pg=pages.extract_text()
        if pg:
            text+=pg+"\n"
    return text

#parse resume


class Experience(BaseModel):
    company: str | None = None # optional field if nothing then none
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = []

class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []

resume_schema=Resume.model_json_schema()

def parse_resume(resume_text):
    system_prompt = f"""
    You are an expert resume parser.

    Extract information from the resume based on its meaning,
    not only based on exact section headings.

    Different resumes may use different headings.

    For example:
    - Experience
    - Professional Experience
    - Work History
    - Employment
    - Internships

    These may all contain relevant experience.

    Skills may also appear in the skills section, work experience,
    internships or projects.

    Return ONLY valid JSON matching this schema:

    {resume_schema}

    Important rules:

    1. Do not invent information.
    2. If a value is not available, return null.
    3. If a list has no information, return an empty list.
    4. Include internships inside experiences.
    5. Extract skills mentioned across the entire resume.
    """
    user_prompt = f"""
    Parse the following resume:

    {resume_text}
    """
    message_system={
        "role" : "system",
        "content" : system_prompt
    }
    message_user={
        "role" : "user",
        "content" : user_prompt
    }
    messages=[message_system, message_user]
    response_format={
        "type": "json_object"
    }
    response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
    raw_output = response.choices[0].message.content
    data = json.loads(raw_output)
    resume = Resume(**data)
    return resume

#chatbot ke cheeeze
#question ayega string format me toh schema vaise banao

class ChatRequest(BaseModel):
    question: str

def ask_candidate(question: str, resume: Resume):

    system_prompt = f"""
You are an AI assistant representing a job candidate.

Below is everything you know about the candidate.

{resume.model_dump_json(indent=2)}

Rules:

1. Answer only using this information.

2. Never hallucinate.

3. If information is unavailable,
say

"I don't have enough information to answer that."

4. Be professional.

5. Answer as if HR is interviewing this candidate.

6. when answering, the answer should not have * at all anywhere.
"""

    response = client.chat.completions.create(

        model=model,

        messages=[

            {
                "role":"system",
                "content":system_prompt
            },

            {
                "role":"user",
                "content":question
            }

        ]

    )
    return response.choices[0].message.content



@app.get("/") ## yeh hamesha home ke just upar hona chahiye agar nahi hua app will not work

def home():
    #read_res=resume_parser(Path("resume.pdf"))
    #print(read_res) #terminal pe print hoga not web, uspe karne ke liye do in return
    #resume=parse_resume(read_res)
    #print(resume.model_dump_json(indent=2))
    return {
        "message":"resume parsed"
    }
#abhi ke liye itna hi likhna hai later we will add our frontend and all but imp run karne ke liye we need uvicorn and why --reload, instead of co
#continously running again and again, we make our changes and just save and check so needed

#alag chat ke liye alag page/ name dena hai weblink ko how?
read_res=resume_parser(Path("resume.pdf"))
resume=parse_resume(read_res)

@app.post("/chat") #why post: isme koi request aati hai uska ans karte hai ut get me koi as such request nahi hota toh directly homepage, chat 
# ke liye toh alag hai
def chat(request: ChatRequest):
    answer=ask_candidate(request.question,resume)
    return{
        "answer":answer
    }
        