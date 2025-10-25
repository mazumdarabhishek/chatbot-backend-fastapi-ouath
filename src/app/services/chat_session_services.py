from app.models.chats import ChatSession, ChatTranscript
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_session
from sqlalchemy.orm import Session

from app.core.app_logger import setup_daily_logger
import traceback
logger = setup_daily_logger(logger_name=__name__)

def get_sessions_be_user(session: Session, user_id: int, page: int = 1, page_size: int = 10):
    try:
        if page < 1:
            page = 1
        offset = (page - 1) * page_size
        
        entries = session.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc())\
            .offset(offset).limit(page_size).all()
        
        allowed_columns = ["thread_id", "created_at"]
        list_content = [entry.to_dict(allowed_columns) for entry in entries]

        return list_content

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error in get_sessions_by_user: {e}")
        logger.error(traceback.format_exc())
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_sessions_by_user: {e}")
        logger.error(traceback.format_exc())
        return []

def get_transcripts_by_thread(session: Session, thread_id: str,page: int = 1, page_size: int = 10):
    try:
        if page < 1:
            page = 1
        
        offset = (page - 1) * page_size
        entries = session.query(ChatTranscript).filter(ChatTranscript.thread_id == thread_id)\
            .order_by(ChatTranscript.created_at.asc())\
            .offset(offset)\
                    .limit(page_size)\
                    .all()
        allowed_columns = ["message", "sender", "created_at"]
        list_content = [entry.to_dict(allowed_columns) for entry in entries]
        return list_content
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error in get_transcripts_by_thread: {e}")
        logger.error(traceback.format_exc())
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_transcripts_by_thread: {e}")
        logger.error(traceback.format_exc())
        return []

# delete a session and transcripts by thread_id
def delete_session_by_thread(session: Session, thread_id: str):
    try:
        chat_session = session.query(ChatSession).filter(ChatSession.thread_id == thread_id).first()
        if chat_session:
            session.delete(chat_session)
            session.commit()
            return True
        else:
            logger.info(f"No chat session found with thread_id: {thread_id}")
            return False
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error in delete_session_by_thread: {e}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"Unexpected error in delete_session_by_thread: {e}")
        logger.error(traceback.format_exc())
        return False