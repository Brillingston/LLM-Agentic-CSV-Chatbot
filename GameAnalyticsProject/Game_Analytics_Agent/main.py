import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent import GameAnalyticsAgent
import uvicorn

app = FastAPI(
    title="Game Analytics Agent",
    description="AI-powered agent that answers analytical questions about Steam games.",
    version="1.0.0"
)

agent = GameAnalyticsAgent()

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Game Analytics Agent is running. POST to /game/analytics to query."}

@app.post("/game/analytics")
def game_analytics(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        result = agent.answer(request.query)
        return {"response": result["response"], "metadata": result["metadata"]}
    except Exception as e:
        error_detail = traceback.format_exc()
        print("=== ERROR ===")
        print(error_detail)
        print("=============")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": error_detail}
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
