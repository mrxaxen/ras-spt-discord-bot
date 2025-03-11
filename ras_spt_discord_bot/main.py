import os

from httpx import Client
from discord import InteractionResponseType, InteractionType
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv

load_dotenv()

CMD_PING_SPT_SERVER = "ping"
RAS_SPT_SERVER_URL_PING = os.getenv('RAS_SPT_SERVER_URL_PING', default='')

app = FastAPI()
client = Client()


@app.post('/interactions')
async def interactions(request: Request):
    id, req_type, data = await request.body()

    if req_type == InteractionType.ping:
        return {"type": InteractionResponseType.pong}

    if req_type == InteractionType.application_command:
        if data == CMD_PING_SPT_SERVER:
            try:
                ping_response = client.get(url=RAS_SPT_SERVER_URL_PING)
                is_online = "ONLINE" if ping_response.status_code == 200 else "OFFLINE"
            except Exception:
                is_online = "OFFLINE"

            return {
                "type": InteractionResponseType.channel_message,
                "data": {
                    "content": f"The server is {is_online} at the moment."
                }
            }
        else:
            print(f"Unknown command: {data}")
            raise HTTPException(status_code=400, detail='Unknown command')

    print(f"Unknown interaction type: {req_type}")
    raise HTTPException(status_code=400, detail='Unknown interaction type')
