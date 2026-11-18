from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI
from google.genai import types

load_dotenv()
client= genai.Client()

app=FastAPI()

class Review(BaseModel):
    text:str

class Analysis(BaseModel):
    label:str
    score:int
    theme:str

@app.post("/analyze")
def analyze(review: Review):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=(
            "Analyze the following review and provide a label, score, and theme:\n\n"
            "label must be one of the following: positive, negative, neutral\n"
            "score must be an integer between 1(very bad) and 10(very good)\n"
            "theme must be one of the following: product quality, customer service, delivery experience, pricing, overall satisfaction\n\n"
            f"Review: {review.text}\n\n"
        ),

        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Analysis,
        ),
    )
    return response.parsed