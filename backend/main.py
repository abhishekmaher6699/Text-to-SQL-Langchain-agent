from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

import pandas as pd
from io import StringIO
from dotenv import load_dotenv
from pydantic import BaseModel
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_community.utilities import SQLDatabase
from psycopg import Connection

from backend.databases.operations import create_connection, show_all_tables

load_dotenv()

app = FastAPI()

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

CHECKPOINT_DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_URI = "sqlite:///backend/databases/tables.db"

db = SQLDatabase.from_uri(DB_URI)
dialect = db.dialect
table_info = db.get_table_info()
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    table_name: str


@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))

        table_name = file.filename.rsplit('.', 1)[0]

        all_tables = show_all_tables()
        if table_name in all_tables:
            return {"message": f"Table '{table_name}' already exists. Please choose a different name.", "table_name": table_name}

        else:           
            engine = create_connection()
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)

            return {"message": f"CSV file uploaded successfully! Data saved in table '{table_name}'.", "table_name": table_name}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post("/chat/")
def chat(request: ChatRequest):
    
    try:
        from backend.agent_comp.agent import workflow

        with Connection.connect(CHECKPOINT_DB_URI, **connection_kwargs) as conn:

            print("In connection")
            checkpointer = PostgresSaver(conn)
            checkpointer.setup()
            app = workflow.compile(checkpointer=checkpointer)

            config = {"configurable": {"thread_id": request.thread_id}}

            ans = app.invoke({"messages": [request.message], "table_name": request.table_name}, config=config)
            
            response = {"reply": ans["answer"], "thread_id": request.thread_id}

            return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/get_all_tables/")
def get_tables():
    # print("In get tables")
    try:
        tables = show_all_tables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def main():
    return {"message": "Welcome to the TEXT-2-SQL API!"}