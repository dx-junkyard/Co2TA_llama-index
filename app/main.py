from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import initialize_database, get_markdown_by_id, pdf_to_markdown
from utils import get_application_form

app = FastAPI()

# データベースの初期化
initialize_database()

class UserInput(BaseModel):
    text: str

@app.post("/get_form/")
async def get_form(user_input: UserInput):
    try:
        markdown_content = get_application_form(user_input.text)
        return {"markdown": markdown_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))