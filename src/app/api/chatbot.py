from fastapi import APIRouter, Depends, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.schemas.common import APIResponse, ChatResponse
from app.services.chatbot_services import build_chat_graph
from app.schemas.chat import AgentState, ChatRequest, ChatSessionRequest
from app.services.auth_services import get_current_user
from app.core.database import get_session
from typing import Optional
from app.utils.chat_background_utils import *
from app.services.chat_session_services import *
import uuid

from app.core.app_logger import setup_daily_logger
logger = setup_daily_logger(logger_name=__name__)

chatbot_app = APIRouter(prefix="/chatbot")

@chatbot_app.post("/chat")
async def chat_endpoint(request: Request, background_tasks: BackgroundTasks, chat_request: Optional[ChatRequest] = None, current_user: str = Depends(get_current_user),
                        session: Session = Depends(get_session)):
    
    try:
        if isinstance(current_user, APIResponse):
            return current_user
        
        if chat_request is None:
            thread_id = uuid.uuid4()
            
            input_state = AgentState(
                messages=[],
                user_input= None,
                turns_to_compress=0,
            )
            
            session_content = {
                "id": str(uuid.uuid4()),
                "user_id": current_user.id,
                "thread_id": str(thread_id),
                "created_at": datetime.now(timezone.utc)}
            
            # Store the session_id for later use
            session_id = session_content["id"]
            background_tasks.add_task(session_writer, session, session_content)
        
        else:
            input_state = {"user_input": chat_request.user_input}
            thread_id = chat_request.thread_id
            
            # Get the session_id from the database using thread_id
            chat_session = session.query(ChatSession).filter(ChatSession.thread_id == str(thread_id)).first()
            if not chat_session:
                return APIResponse(status=status.HTTP_404_NOT_FOUND, 
                                 message="Chat session not found", data=None)
            session_id = chat_session.id

            background_tasks.add_task(transcript_writer, session, {"id": str(uuid.uuid4()), "thread_id": session_id, "message": chat_request.user_input,
                                                                    "sender": "User", "created_at": datetime.now(timezone.utc)})
            
        state = await request.app.state.graph.ainvoke(input_state, 
                                                        config={"configurable": {"thread_id": thread_id}})
            

        background_tasks.add_task(transcript_writer, session, {"id": str(uuid.uuid4()), "thread_id": session_id, "message": state["messages"][-1].content,
                                                                "sender": "AI", "created_at": datetime.now(timezone.utc)})

        return APIResponse(status=status.HTTP_200_OK, message="Chat response generated successfully",
                           data=ChatResponse(response=state["messages"][-1].content, thread_id=str(thread_id)).model_dump())

    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}")
        logger.error(traceback.format_exc())
        return APIResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                           message="Internal Server Error", data=None)
        

@chatbot_app.post("/get_sessions")
async def get_sessions_endpoint(data: ChatSessionRequest, current_user: str = Depends(get_current_user),
                               session: Session = Depends(get_session)):
    try:
        if isinstance(current_user, APIResponse):
            return current_user
        
        sessions = get_sessions_be_user(session, current_user.id, data.page, data.page_size)
        
        return APIResponse(status=status.HTTP_200_OK, message="Chat sessions retrieved successfully", data=sessions)
    
    except Exception as e:
        logger.error(f"Error in get_sessions_endpoint: {e}")
        logger.error(traceback.format_exc())
        return APIResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                           message="Internal Server Error", data=None)

@chatbot_app.post("/get_transcripts")
async def get_transcripts_endpoint(data: ChatSessionRequest, current_user: str = Depends(get_current_user),
                                   session: Session = Depends(get_session)):
    try:
        if isinstance(current_user, APIResponse):
            return current_user
        
        transcripts = get_transcripts_by_thread(session, data.thread_id, data.page, data.page_size)
        
        return APIResponse(status=status.HTTP_200_OK, message="Chat transcripts retrieved successfully", data=transcripts)
    
    except Exception as e:
        logger.error(f"Error in get_transcripts_endpoint: {e}")
        logger.error(traceback.format_exc())
        return APIResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                           message="Internal Server Error", data=None)

@chatbot_app.delete("/delete_session/{thread_id}")
async def delete_session_endpoint(thread_id: str, current_user: str = Depends(get_current_user),
                                  session: Session = Depends(get_session)):
    try:
        if isinstance(current_user, APIResponse):
            return current_user
        
        success = delete_session_by_thread(session, thread_id)
        if success:
            return APIResponse(status=status.HTTP_204_NO_CONTENT, message="Chat session deleted successfully", data=None)
        else:
            return APIResponse(status=status.HTTP_404_NOT_FOUND, message="Chat session not found", data=None)
    
    except Exception as e:
        logger.error(f"Error in delete_session_endpoint: {e}")
        logger.error(traceback.format_exc())
        return APIResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                           message="Internal Server Error", data=None)