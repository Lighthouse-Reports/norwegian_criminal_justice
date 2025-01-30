import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
from config import db_config
from datetime import datetime

#client = db_config.LOCAL_CLIENT
db = db_config.DB_LOCAL_DOMMEDAG_OUTPUT
collection = db[f"{datetime.now().strftime('%Y_%m_%d')}_dommer"]