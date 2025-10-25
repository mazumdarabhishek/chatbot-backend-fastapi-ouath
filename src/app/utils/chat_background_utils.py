from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict
import traceback
from datetime import datetime, timezone
from app.models.chats import ChatTranscript, ChatSession

from app.core.app_logger import setup_daily_logger
logger = setup_daily_logger(logger_name=__name__)

def session_writer(session: Session, content : Dict):
    
    try:
        new_entry = ChatSession(**content)
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        
        logger.debug(f"Chat Session created with id: {new_entry.id}")
    
    except SQLAlchemyError as e:
        # Roll back the session in case of any database error
        session.rollback()
        logger.warning(f"Failed to save record. Rolling back transaction. Error: {e}")
        logger.error(traceback.format_exc())
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")
        logger.error(traceback.format_exc())

def session_updater(session: Session, thread_id: str, **kwargs):
    try:
        existing_entry = session.query(ChatSession).filter(ChatSession.id == thread_id).first()
        
        if existing_entry:
            for key, value in kwargs.items():
                setattr(existing_entry, key, value)
            
            existing_entry.updated_at = datetime.now(timezone.utc)
            session.add(existing_entry)
            session.commit()
            session.refresh(existing_entry)
            logger.debug(f"Chat Session with id: {thread_id} updated successfully.")
        else:
            logger.warning(f"No Chat Session found with id: {thread_id}. Update skipped.")
    
    except SQLAlchemyError as e:
        session.rollback()
        logger.warning(f"Failed to save record. Rolling back transaction. Error: {e}")
        logger.error(traceback.format_exc())
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")
        logger.error(traceback.format_exc())
    

def transcript_writer(session: Session, content : Dict):
    try:
        new_entry = ChatTranscript(**content)
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        
        logger.debug(f"Chat Transcript created with id: {new_entry.id}")
    
    except SQLAlchemyError as e:
        session.rollback()
        logger.warning(f"Failed to save record. Rolling back transaction. Error: {e}")
        logger.error(traceback.format_exc())
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")
        logger.error(traceback.format_exc())       