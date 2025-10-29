import sys
import os

# Ensure the 'server' directory (which contains the 'app' package) is on sys.path
_server_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server'))
if _server_dir not in sys.path:
    sys.path.insert(0, _server_dir)

from app.database.session import engine
from app.models.prompt import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating all database tables...")
    try:
        # The magic happens here: Base.metadata contains all the table definitions
        # and create_all connects to the engine and creates them.
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully!")
    except Exception as e:
        logger.error(f"An error occurred while creating tables: {e}")
        # Depending on the error, you might want to raise it or handle it differently
        raise

if __name__ == "__main__":
    init_db()