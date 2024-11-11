"""
This script utilizes the Google Generative AI (genai) API to analyze interview transcripts for fairness and bias. 
It generates a fairness score between 0 and 1, where 0 is very biased and unfair, and 1 is unbiased and fair.

The script configures the genai API with an API key, sets up generation configurations, and defines safety 
settings to block certain categories of harmful content in the AI responses.

Attributes:
    generation_config (dict): Configuration settings for the generative AI model, including temperature, 
                              token limit, and top-p/top-k sampling values.
    safety_settings (list): Safety configuration settings to prevent responses in categories like harassment, 
                            hate speech, sexually explicit, and dangerous content.
    system_prompt (str): Initial prompt that provides instructions to the AI model for evaluating fairness 
                         and bias in an interview transcript.

Functions:
    score_transcript(transcript: str, position: str) -> str:
        Analyzes the provided interview transcript for fairness and bias. Generates a fairness score and 
        an explanation based on the model's analysis.

        Parameters:
            transcript (str): The transcript of the interview to be evaluated.
            position (str): The job position title related to the interview.

        Returns:
            str: A response string containing the fairness score and explanation from the model.
"""


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

def score_transcript(transcript: str, position: str)->str:
    """Analyzes the provided interview transcript for fairness and bias. Generates a fairness score and 
        an explanation based on the model's analysis.

    Args:
        transcript: The transcript of the interview to be evaluated.
        position: The job position title related to the interview.

    Returns:
        A response string containing the fairness score and explanation from the model.
    """
    model = genai.GenerativeModel(model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
     )
    
    prompt = system_prompt + "This interview is for a " + position + " position: " + transcript + "."
    prefix = "Your fairness score for this interview is"
    response = model.generate_content(prompt)
    return prefix + response.text.replace('*', '').replace('#', '').replace('Score:', '')
