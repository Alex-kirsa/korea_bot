import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from bot.db import Repo
from bot.utils.constants import TagType
from configreader import config

app = FastAPI()

engine = create_async_engine(str(config.postgredsn), future=True, echo=False)
db_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Tag(BaseModel):
    id: int
    tag: str


class Tags(BaseModel):
    status: int = 200
    tags_list: list[Tag]


origins = [
    "https://webapp-forms.netlify.app",
    "http://localhost",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# app.add_middleware(HTTPSRedirectMiddleware)


@app.get('/api/tags', description="Для отримання тегів", response_model=Tags)
async def get_tags(tag_type: TagType):
    async with db_factory() as session:
        repo = Repo(session)
        tags = await repo.post_repo.get_tags(tag_type)
        return {'status': 200, 'tags_list': [{'id': tag.id, 'tag': tag.tag} for tag in tags] if tags else []}


if __name__ == "__main__":
    uvicorn.run(app, port=config.api_port, host=config.api_host)
