from flask import Flask, request
from llama_index.llms.gemini import Gemini
from llama_index.core import SQLDatabase, VectorStoreIndex, SimpleDirectoryReader, Settings, load_index_from_storage
import os
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.embeddings.gemini import GeminiEmbedding

app = Flask(__name__)
tables = ["customers", "employees", "offices"]


class Config:
    def __init__(self):
        load_dotenv()
        self.tidb_host = os.getenv("TIDB_HOST", "127.0.0.1")
        self.tidb_port = int(os.getenv("TIDB_PORT", "4000"))
        self.tidb_user = os.getenv("TIDB_USER", "root")
        self.tidb_password = os.getenv("TIDB_PASSWORD", "")
        self.tidb_db_name = os.getenv("TIDB_DB_NAME", "test")
        self.ca_path = os.getenv("CA_PATH", "")


def get_db_engine():
    config = Config()
    dsn = URL.create(
        drivername="mysql+pymysql",
        username=config.tidb_user,
        password=config.tidb_password,
        host=config.tidb_host,
        port=config.tidb_port,
        database=config.tidb_db_name,
    )
    connect_args = {}
    if config.ca_path:
        connect_args = {
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
            "ssl_ca": config.ca_path,
        }
    return create_engine(
        dsn,
        connect_args=connect_args,
    )


engine = get_db_engine()
Session = sessionmaker(bind=engine)
Base = declarative_base()
sql_database = SQLDatabase(engine, include_tables=tables)
llm = Gemini(model="models/gemini-1.5-flash-001", api_key=os.getenv("GOOGLE_API_KEY"))
Settings.llm = llm
Settings.embed_model = GeminiEmbedding(
    model_name="models/embedding-001", api_key=os.getenv("GOOGLE_API_KEY")
)


@app.get("/")
def index():
    return {
       "message": "Ok"
    }, 200


@app.post("/sql-query-response")
def getSQLQueryResponse():
    body = request.json
    resp = Gemini().complete(body.get("question"))
    return {
        "message": str(resp)
    }


@app.post("/sql-text-to-query")
def getSQLTextToQuery():
    body = request.json
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database, tables=tables, llm=llm
    )
    query_str = body.get("question")
    response = query_engine.query(query_str)
    return {
        "message": str(response)
    }


if __name__ == "__main__":
    app.run(debug=True, port=8080)

