import dotenv
import os

dotenv.load_dotenv()
print(os.getenv("DATABASE_URI"))
# print(dotenv.getenv("DATABASE_URI"))