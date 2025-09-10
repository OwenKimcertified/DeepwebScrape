from dotenv import load_dotenv
import os 

load_dotenv()

HOST = os.getenv("HOST")
DB = os.getenv("DB")
COLLECTION = os.getenv("COLLECTION")