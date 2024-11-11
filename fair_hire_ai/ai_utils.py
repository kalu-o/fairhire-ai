import google.generativeai as genai
import os


genai.configure(api_key=os.environ["API_KEY"])

generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

system_prompt = """You are an expert that analyzes interview transcripts and assigns a score between 0 and 1 
for fairness/unbiased (0 very biased and unfair, 1 unbiased and fair). Score the following transcript and 
explain your decision. """

def score_transcript(transcript: str, position: str):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
     )
    
    prompt = system_prompt + "This interview is for a " + position + " position: " + transcript + "."
    prefix = "Your fairness score for this interview is"
    response = model.generate_content(prompt)
    return prefix + response.text.replace('*', '').replace('#', '').replace('Score:', '')
