import os
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from services.ai_service import process_query
from services.property_service import get_hotels_in_dubai, search_hotels

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))  # Default to 4000 if PORT not set

@app.get("/")
async def root():
    
    return {"message": "Property Search API is running"}

@app.post("/search")
async def search(data: dict = Body(...)):
    query = data.get("query")
    
    # Step 1: Extract filters using AI
    filters = await process_query(query)
    print(query)
    print(filters)
    
    # Step 2: Search properties using Amadeus API
    properties = search_hotels(filters)
    print(properties)
    
    return {
        "response": f"Here are some options in {filters.get('location')}",
        "filters": filters,
        "properties": properties
    }
@app.get("/search/dubai")
async def dubai_search():
    return get_hotels_in_dubai()