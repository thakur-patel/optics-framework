# api.py
import json
import uuid
import asyncio
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from optics_framework.common.session_manager import SessionManager, Session
from optics_framework.common.execution import ExecutionEngine
from optics_framework.common.logging_config import logger, apply_logger_format_to_all

app = FastAPI(title="Optics Framework API", version="1.0")
session_manager = SessionManager()


class SessionConfig(BaseModel):
    """Schema for session creation."""
    driver_sources: list[str]
    app_param: dict = {}
    elements_sources: list[str] = []
    text_detection: list[str] = []
    image_detection: list[str] = []
    project_path: Optional[str] = None


class ExecuteRequest(BaseModel):
    """Schema for execution requests."""
    mode: str  # "batch", "dry_run", or "keyword"
    test_case: Optional[str] = None
    keyword: Optional[str] = None
    params: list[str] = []


@app.post("/v1/sessions")
async def create_session(config: SessionConfig):
    """Creates a new session."""
    try:
        session_config = config.dict()
        session_id = session_manager.create_session(session_config)
        logger.info(
            f"Created session {session_id} with config: {session_config}")
        return {"session_id": session_id, "status": "created"}
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=500, detail=f"Session creation failed: {e}")


@app.post("/v1/sessions/{session_id}/execute")
async def execute(
    session_id: str,
    request: ExecuteRequest,
    background_tasks: BackgroundTasks
):
    """Triggers execution in a session."""
    session = session_manager.get_session(session_id)
    if not session:
        logger.error(f"Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    execution_id = str(uuid.uuid4())
    logger.info(
        f"Starting execution {execution_id} for session {session_id} with request: {request.dict()}")

    engine = ExecutionEngine(session_manager)
    background_tasks.add_task(
        run_execution,
        engine,
        session_id,
        execution_id,
        request.mode,
        request.test_case,
        request.keyword,
        request.params,
        session.event_queue
    )
    return {"execution_id": execution_id, "status": "started"}


@app.get("/v1/sessions/{session_id}/events")
async def stream_events(session_id: str):
    """Streams execution events for a session."""
    session = session_manager.get_session(session_id)
    if not session:
        logger.error(f"Session not found for event streaming: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info(f"Starting event stream for session {session_id}")
    return EventSourceResponse(event_generator(session))


@app.delete("/v1/sessions/{session_id}")
async def delete_session(session_id: str):
    """Terminates a session."""
    try:
        session_manager.terminate_session(session_id)
        logger.info(f"Terminated session: {session_id}")
        return {"status": "terminated"}
    except Exception as e:
        logger.error(f"Failed to terminate session {session_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Session termination failed: {e}")


@apply_logger_format_to_all("user")
async def run_execution(
    engine: ExecutionEngine,
    session_id: str,
    execution_id: str,
    mode: str,
    test_case: Optional[str],
    keyword: Optional[str],
    params: list[str],
    event_queue: Optional[asyncio.Queue]
):
    """Runs the requested execution in the background."""
    session = session_manager.get_session(session_id)
    if not session or not event_queue:
        logger.error(
            f"Session {session_id} not found or invalid during execution {execution_id}")
        if event_queue:
            await event_queue.put({
                "execution_id": execution_id,
                "status": "ERROR",
                "message": "Session not found or invalid"
            })
        return

    try:
        await engine.execute(
            session_id=session_id,
            mode=mode,
            test_case=test_case,
            keyword=keyword,
            params=params,
            event_queue=event_queue
        )
        logger.info(f"Execution {execution_id} completed successfully")
    except Exception as e:
        logger.error(f"Execution {execution_id} failed: {e}")
        await event_queue.put({
            "execution_id": execution_id,
            "status": "FAIL",
            "message": f"Execution failed: {str(e)}"
        })


@apply_logger_format_to_all("user")
async def event_generator(session: Session):
    """Generates SSE events from the session's event queue."""
    while True:
        try:
            event = await session.event_queue.get()
            logger.debug(
                f"Streaming event for session {session.session_id}: {event}")
            yield {"data": json.dumps(event)}
        except Exception as e:
            logger.error(
                f"Error in event streaming for session {session.session_id}: {e}")
            yield {"data": json.dumps({"status": "ERROR", "message": f"Event streaming failed: {e}"})}
            break


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
