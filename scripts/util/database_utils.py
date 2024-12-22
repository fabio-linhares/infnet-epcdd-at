import sqlite3
import time
import logging
import os

# Use importação relativa
from .file_utils import acquire_lock, release_lock

logger = logging.getLogger(__name__)


def get_db_connection(max_attempts=5, retry_delay=1):
    DB_NAME = os.getenv('DB_NAME', 'chat_history.db')
    for attempt in range(max_attempts):
        try:
            conn = sqlite3.connect(DB_NAME, timeout=60)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            if attempt == max_attempts - 1:
                logger.error(f"Failed to connect to database after {max_attempts} attempts: {str(e)}")
                raise
            time.sleep(retry_delay)

def close_all_connections():
    for conn in sqlite3.connect(os.getenv('DB_NAME', 'chat_history.db')).execute("PRAGMA database_list"):
        db_path = conn[2]
        if db_path != ':memory:':
            sqlite3.connect(db_path, uri=True).close()

def initialize_database():
    try:
        lock_fd = acquire_lock('db.lock')
        if lock_fd:
            try:
                with get_db_connection() as conn:
                    c = conn.cursor()
                    c.execute(os.getenv('DB_CREATE_TABLE_QUERY'))
                    conn.commit()
            finally:
                release_lock(lock_fd)
        else:
            logger.warning("Could not acquire exclusive access to the database. Please try again.")
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise

def save_chat_history(user_input, full_response, max_attempts=5):
    for attempt in range(max_attempts):
        lock_fd = acquire_lock('db.lock')
        if lock_fd:
            try:
                with get_db_connection() as conn:
                    c = conn.cursor()
                    c.execute("INSERT INTO chat_history (user_input, ai_response) VALUES (?, ?)",
                              (user_input, full_response))
                    conn.commit()
                break
            except sqlite3.Error as e:
                if attempt == max_attempts - 1:
                    logger.warning(f"Failed to save chat history after {max_attempts} attempts: {str(e)}")
                    raise
            finally:
                release_lock(lock_fd)
        else:
            if attempt == max_attempts - 1:
                logger.warning("Could not acquire exclusive access to save chat history. Please try again.")
                raise
        time.sleep(1)