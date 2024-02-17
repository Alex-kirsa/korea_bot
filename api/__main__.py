from typing import Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

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


@app.get('/tags', description="Для отримання тегів", response_model=Tags)
async def get_tags(tag_type: TagType):
    async with db_factory() as session:
        repo = Repo(session)
        tags = await repo.post_repo.get_tags(tag_type)
        print(tags)
        return {'status': 200, 'tags_list': [{'id': tag.id, 'tag': tag.tag} for tag in tags] if tags else []}


if __name__ == "__main__":
    uvicorn.run(app, port=config.api_port, host=config.api_host)
