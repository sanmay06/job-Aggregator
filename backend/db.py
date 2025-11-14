import os

USE_MONGO = os.getenv("USE_MONGO", "false").lower() == "true"

if USE_MONGO:
    from database.mongodb import *
else:
    from database.postgres import *
