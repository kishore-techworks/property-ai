import os
import json
import re
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

async def process_query(query: str):
    prompt = ChatPromptTemplate.from_template("""
    Extract the following details from this query:
    "{query}"
    Return only valid JSON with these keys:
    location (city), check_in (YYYY-MM-DD), check_out (YYYY-MM-DD), guests (int), max_price (int or null).
    
    Example output:
    {{"location": "Dubai", "check_in": "2025-08-10", "check_out": "2025-08-15", "guests": 2, "max_price": 200}}
    """)  # ✅ Double curly braces inside example JSON

    formatted_prompt = prompt.format(query=query)  # ✅ Only query is replaced
    response = await llm.apredict(formatted_prompt)

    text = response.strip()
    print("Raw LLM Response:", text)

    import re
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"location": None, "check_in": None, "check_out": None, "guests": None, "max_price": None}
