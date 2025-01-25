from crewai_tools import SerperDevTool
from crewai import LLM
import os

"""LLM"""
llm = LLM(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0.7,       
    timeout=120,           
    max_tokens=1000,      
    top_p=0.9,           
    frequency_penalty=0.1, 
    presence_penalty=0.1,  
    seed=42               
)

"""SerperDevTool"""
serper_dev_tool = SerperDevTool(
    country="fr",
    locale="fr",
    location="Paris, Paris, Ile-de-France, France",
    n_results=2,
)