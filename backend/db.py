import os

# For this project we only use the PostgreSQL backend. The MongoDB
# implementation is retained for completeness but is not imported
# automatically to avoid a hard dependency on pymongo.
from database.postgres import *
