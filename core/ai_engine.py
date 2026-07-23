from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pdfplumber
import os

def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )

def read_cv(file_path: str) -> str:
    """Read text from PDF CV."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def analyze_cv(cv_text: str, job_description: str) -> dict:
    """Analyze CV against job description."""
    llm = get_llm()
    parser = StrOutputParser()

    # Extract info
    extract_prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract key info from CV.
         Return ONLY in this format:
         Skills: [comma separated]
         Experience: [years and role]
         Summary: [2 sentences]"""),
        ("human", "CV:\n{cv}")
    ])

    # Score candidate
    score_prompt = ChatPromptTemplate.from_messages([
        ("system", """Score this candidate 0-100 for the job.
         Return ONLY in this format:
         Score: [number]/100
         Recommendation: [Shortlist/Reject/Consider]
         Reason: [one line]"""),
        ("human", "Job:\n{job}\n\nCV:\n{cv}")
    ])

    extract_chain = extract_prompt | llm | parser
    score_chain = score_prompt | llm | parser

    extracted = extract_chain.invoke({"cv": cv_text})
    scored = score_chain.invoke({
        "job": job_description,
        "cv": cv_text
    })

    # Parse score
    score = 0
    recommendation = "Consider"
    for line in scored.split("\n"):
        if "Score:" in line:
            try:
                score = int(line.split(":")[1].strip().split("/")[0])
            except:
                score = 0
        if "Recommendation:" in line:
            recommendation = line.split(":")[1].strip()

    return {
        "summary": extracted,
        "score": score,
        "recommendation": recommendation
    }