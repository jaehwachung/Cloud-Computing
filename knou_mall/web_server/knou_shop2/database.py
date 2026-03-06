from sqlalchemy import create_engine, URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
from os import getenv

load_dotenv("/opt/shop2.env")

DB_HOST = getenv("DB_HOST")
DB_USER = getenv("DB_USER")
DB_NAME = getenv("DB_NAME")
VAULT_URL = getenv("VAULT_URL")

credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)

retrieved_secret = client.get_secret("MALL-DB-PASSWORD")
DB_PASSWD = retrieved_secret.value

url_object = URL.create("postgresql+pg8000",
    username=DB_USER,
    password=DB_PASSWD,
    host=DB_HOST,
    database=DB_NAME)

engine = create_engine(url_object, echo=False)
db_session = scoped_session(sessionmaker(autocommit=False,
                                        autoflush=False,
                                        bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import knou_shop2.models
    Base.metadata.create_all(bind=engine)
