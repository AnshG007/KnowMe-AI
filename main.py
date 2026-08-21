# from pathlib import Path
# from dotenv import load_dotenv # type: ignore
# from groq import Groq # type: ignore
# import os
# import re
# from time import sleep
# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()
# load_dotenv()
# my_api_key = os.getenv("GROQ_API_KEY") # type: ignore
# if not my_api_key:
#     raise ValueError("Api key kaha hai?")
# client = Groq(api_key = my_api_key)
# model = 'GPT OSS 120B'
# # -------------------------------


# class Question(BaseModel):
#     question :str
# with open("profile.txt", "r", encoding="utf-8") as file:
#     profile = file.read()
# #print(profile)
# @app.get("/")
# def home():
#     return {"message":"welcome from the chatbot"}


# @app.post("/ask")
# def ask_ai(data:Question):
#     sys_prompt = """
# You are Ansh Gupta's AI assistant.

# Answer ONLY using the information below.

# If the answer is not present,
# reply exactly:

# I don't know.

# Information:

# {profile}

# Question:

# {data.question}

# """
#     message_system = {
#         'role':"system",
#         'content':sys_prompt
#     }
#     message_prompt =  {
#         "role": "user",
#         "content": f"""
# Below is information about a person named Ansh Gupta.

# Your task is to answer the user's question ONLY using the information provided below.

# Rules:
# 1. Do NOT make up information.
# 2. Do NOT assume anything that is not written.
# 3. If the answer is not available, reply exactly:
#    "I don't know."
# 4. Answer naturally and professionally.
# 5. If asked to introduce Ansh, summarize his education, experience, skills, and projects from the information below.


# =========================
# INFORMATION
# =========================

# {profile}

# =========================
# USER QUESTION
# =========================

# {data.question}

# =========================
# ANSWER
# =========================
# """
#     }

#     messages = [message_system , message_prompt]
#     response = client.chat.completions.create(model = model , messages=messages)

#     answer =  response.choices[0].message.content

#     return {
#         "question":data.question,
#         "answer":answer
#     }



from pathlib import Path
from dotenv import load_dotenv # type: ignore
from groq import Groq # type: ignore
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

app = FastAPI()

# 1. CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Find absolute path of project directory
BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML_PATH = BASE_DIR / "index.html"
PROFILE_PATH = BASE_DIR / "profile.txt"

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("Api key not found in .env file.")

client = Groq(api_key=my_api_key)
model = 'GPT OSS 120B'

# Read profile.txt safely
if PROFILE_PATH.exists():
    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        profile = file.read()
else:
    profile = "Ansh Gupta is a software developer."


class Question(BaseModel):
    question: str


# Serve index.html dynamically
@app.get("/", response_class=HTMLResponse)
def home():
    if INDEX_HTML_PATH.exists():
        return FileResponse(INDEX_HTML_PATH, media_type="text/html")
    else:
        return HTMLResponse(
            content=f"""
            <h2>❌ index.html not found!</h2>
            <p>Please make sure <b>index.html</b> is saved in this directory:</p>
            <code>{BASE_DIR}</code>
            """, 
            status_code=404
        )


@app.post("/ask")
def ask_ai(data: Question):
    sys_prompt = f"""
You are Ansh Gupta's AI assistant.
Answer ONLY using the information below.
If the answer is not present, reply exactly: "I don't know."

Information:
{profile}
"""

    message_system = {'role': "system", 'content': sys_prompt}
    message_prompt = {
        "role": "user",
        "content": f"""
Below is information about a person named Ansh Gupta.
Your task is to answer the user's question ONLY using the information provided below.
The information below is my permanent profile and is the source of truth.

Whenever I ask about my skills, education, experience, certifications, projects, or career, answer ONLY using this profile.

If the answer exists in the profile, never say "I don't know."
Rules:
1. Do NOT make up information.
2. Do NOT assume anything that is not written.
3. If the answer is not available, reply exactly: "I don't know."
4. Answer naturally and professionally.
5. If asked to introduce Ansh, summarize his education, experience, skills, and projects from the information below.

=========================
INFORMATION
=========================
{profile}

=========================
USER QUESTION
=========================
{data.question}
"""
    }

    try:
        response = client.chat.completions.create(model=model, messages=[message_system, message_prompt])
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error communicating with AI service: {str(e)}"

    return {
        "question": data.question,
        "answer": answer
    }
