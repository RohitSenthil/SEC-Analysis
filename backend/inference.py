import importlib
import json
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.output_parsers import LangchainOutputParser
from llama_index.core.postprocessor import LongContextReorder
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.postprocessor.cohere_rerank import CohereRerank
from pymongo.collection import Collection

# class Risk(BaseModel):
#     risk: str = Field(description="name of risk")
#     impact: str = Field(description="impact of risk")
#     likelihood: str = Field(description="impact of risk")
#     outcome: str = Field(description="explanation of risk")


Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5", trust_remote_code=True
)
# parser = JsonOutputParser(pydantic_object=Risk)
Settings.llm = Anthropic(
    "claude-3-sonnet-20240229",
    temperature=0,
    api_key=os.environ["CLAUDE_API_KEY"],
    # output_parser=LangchainOutputParser(parser),
)
Settings.tokenizer = Anthropic().tokenizer

cohere_rerank = CohereRerank(api_key=os.environ["COHERE_API_KEY"], top_n=5)
reorder = LongContextReorder()


def get_risks(ticker: str, filing: str, db: Collection) -> dict[str, str]:
    date = filing.split("\n", 1)[0][-8:-4]
    new_doc = Document(text=filing, metadata={"Company": ticker, "Date": date})
    index = VectorStoreIndex.from_documents(
        [new_doc],
        embed_model=Settings.embed_model,
        transformations=[
            TokenTextSplitter(
                chunk_size=1024,
                chunk_overlap=20,
                separator="\n",
            ),
            Settings.embed_model,
        ],
    )

    query_engine = index.as_query_engine(
        node_postprocessors=[cohere_rerank, reorder], similarity_top_k=10
    )
    response = str(
        query_engine.query(
            f"Based on the legal and regulatory risks identified from {ticker}'s most recent 10-K filing, determine the key legal/regulatory risks and return a list of the risks associated with their potential impact, likelihood, and outcome in a JSON format for a risk heat map. The acceptable values for impact are negligable, low, moderate, significant, and catastrophic. The acceptable values for likelihood are improbable, remote, occasional, probable, and frequent. For outcome, explain the risk, how it could occur, its potential impact, and where in the filing you derived the analysis from. The format should be [{{risk:..., impact:...,likelihood:...,outcome:...}},...]and there should be no extraneous text. Note that the JSON response must be constructed with double-quotes and not single-quotes.",
        )
    )
    list_start = response.find("[")
    list_end = response.rfind("]")
    risk_factors = json.loads(response[list_start : list_end + 1])
    db.insert_one({ticker: risk_factors})
    return risk_factors
