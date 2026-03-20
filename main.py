import asyncio

import uvicorn
from dotenv import load_dotenv
load_dotenv()

from app.database.engine import create_db


async def main():
    await create_db()
    uvicorn.run(app='app.app:app', host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
