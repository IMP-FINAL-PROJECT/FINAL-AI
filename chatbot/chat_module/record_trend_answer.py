from langchain.llms import GooglePalm
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain.embeddings import SentenceTransformerEmbeddings
from config.Config_list import DATABASE_CONFIG, GOOGLE_CONFIG
from chat_module.sql_prompt import sql_prompt

def get_db_chain():
    db = SQLDatabase.from_uri(
        f"mysql+pymysql://{DATABASE_CONFIG['DB_USER']}:{DATABASE_CONFIG['DB_PASSWORD']}@{DATABASE_CONFIG['DB_HOST']}/{DATABASE_CONFIG['DB_NAME']}",
        sample_rows_in_table_info=3,
    )
    print(db.table_info)

    llm = GooglePalm(google_api_key=GOOGLE_CONFIG['GOOGLE_PALM_API'], temperature=0.1)
    chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

    return chain