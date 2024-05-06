import os
from typing import Annotated

import nest_asyncio
from dotenv import load_dotenv

load_dotenv()

from clean import get_cleaned_filing
from edgar import download_filing
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from inference import get_risks
from pymongo import MongoClient
from visualization import get_table

nest_asyncio.apply()
app = FastAPI()

client = MongoClient(os.environ["MONGO_ATLAS_URL"])
db = client["fintech"]
collection = db["insights"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)


@app.get("/risk")
async def get_risk(ticker: Annotated[str, Query(max_length=5, min_length=3)]):
    risks = collection.find_one({ticker: {"$exists": True}})
    if risks is None:
        filing = download_filing(ticker)
        if filing is None:
            raise HTTPException(status_code=404, detail="Invalid Ticker")
        cleaned_filing = get_cleaned_filing(filing)
        risks = get_risks(ticker, cleaned_filing, collection)
    else:
        risks = risks[ticker]
    visualization = get_table(ticker, risks)
    return {"response": risks, "visualization": visualization}
