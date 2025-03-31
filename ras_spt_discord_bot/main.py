# TODO: Apparently most of this is simply wrong, RTFM....
import os
import zlib

from abc import ABCMeta, abstractmethod
from typing import List
from httpx import Client
from discord import InteractionResponseType, InteractionType
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
from pydantic import TypeAdapter

from ras_spt_discord_bot.models import CurrentPlayer

load_dotenv()

CMD_PING_SPT_SERVER = "spt-ping"
CMD_STOP_SPT_SERVER = "spt-stop"
CMD_START_SPT_SERVER = "spt-start"
CMD_RESTART_SPT_SERVER = "spt-restart"
CMD_CURRENTLY_PLAYING = "spt-playing"
RAS_SPT_WEBSERVER_URL_PING = os.getenv('RAS_SPT_WEBSERVER_URL_PING')
RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING = os.getenv('RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING')
RAS_SPT_SERVER_INTERFACE_URL_STOP = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_STOP')
RAS_SPT_SERVER_INTERFACE_URL_START = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_START')
RAS_SPT_SERVER_INTERFACE_URL_RESTART = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_RESTART')

app = FastAPI()
client = Client()


class SPTCommand(metaclass=ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass: type, /) -> bool:
        attributes = ['matches', 'apply']
        callables = [subclass.matches, subclass.apply]
        return all(hasattr(subclass, attr) for attr in attributes) and all(callable(c) for c in callables) or NotImplemented

    @abstractmethod
    def matches(self, data):
        raise NotImplementedError

    @abstractmethod
    def apply(self):
        raise NotImplementedError


class SPTPing(SPTCommand):

    def matches(self, data):
        if RAS_SPT_WEBSERVER_URL_PING is None:
            raise Exception('Ping endpoint url not defined.')
        return data == CMD_PING_SPT_SERVER

    def apply(self):
        assert RAS_SPT_WEBSERVER_URL_PING
        try:
            response = client.get(url=RAS_SPT_WEBSERVER_URL_PING)
            is_online = "ONLINE" if response.status_code == 200 else "OFFLINE"
        except Exception:
            # TODO: LOG
            is_online = "OFFLINE"

        return {
            "type": InteractionResponseType.channel_message,
            "data": {
                "content": f"The server is {is_online} at the moment."
            }
        }


class SPTStop(SPTCommand):

    def matches(self, data):
        if RAS_SPT_SERVER_INTERFACE_URL_STOP is None:
            raise Exception('Server stop endpoint url not defined.')
        return data == CMD_STOP_SPT_SERVER

    def apply(self):
        assert RAS_SPT_SERVER_INTERFACE_URL_STOP
        try:
            response = client.post(url=RAS_SPT_SERVER_INTERFACE_URL_STOP)
            stop_success = "SUCCESSFUL" if response.status_code == 200 else "FAILED"
        except Exception:
            # TODO: LOG
            stop_success = "FAILED"

        return {
            "type": InteractionResponseType.channel_message,
            "data": {
                "content": f"Server stop is {stop_success}."
            }
        }


class SPTStart(SPTCommand):

    def matches(self, data):
        if RAS_SPT_SERVER_INTERFACE_URL_START is None:
            raise Exception('Server start endpoint url not defined.')
        return data == CMD_START_SPT_SERVER

    def apply(self):
        assert RAS_SPT_SERVER_INTERFACE_URL_START
        try:
            response = client.post(url=RAS_SPT_SERVER_INTERFACE_URL_START)
            start_success = "SUCCESSFUL" if response.status_code == 200 else "FAILED"
        except Exception:
            # TODO: LOG
            start_success = "FAILED"

        return {
            "type": InteractionResponseType.channel_message,
            "data": {
                "content": f"Server start is {start_success}."
            }
        }


class SPTRestart(SPTCommand):

    def matches(self, data):
        if RAS_SPT_SERVER_INTERFACE_URL_RESTART is None:
            raise Exception('Server restart endpoint url not defined.')
        return data == CMD_RESTART_SPT_SERVER

    def apply(self):
        assert RAS_SPT_SERVER_INTERFACE_URL_RESTART
        try:
            response = client.post(url=RAS_SPT_SERVER_INTERFACE_URL_RESTART)
            restart_success = "SUCCESSFUL" if response.status_code == 200 else "FAILED"
        except Exception:
            # TODO: LOG
            restart_success = "FAILED"

        return {
            "type": InteractionResponseType.channel_message,
            "data": {
                "content": f"Server restart is {restart_success}."
            }
        }


# TODO: Finish currently playing
class SPTCurrentlyPlaying(SPTCommand):

    def matches(self, data):
        if RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING is None:
            raise Exception('Currently playing endpoint url not defined.')
        return data == CMD_CURRENTLY_PLAYING

    def apply(self):
        assert RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING
        try:
            response = client.get(url=RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING)
            adapter = TypeAdapter(List[CurrentPlayer])
            current_players = adapter.validate_json(zlib.decompress(response.content))
        except Exception:
            # TODO: LOG
            is_online = "OFFLINE"

        return {
            "type": InteractionResponseType.channel_message,
            "data": {
                "content": f"Current players placeholder text"
            }
        }


@app.post('/interactions')
async def interactions(request: Request):
    id, req_type, data = await request.body()

    if req_type == InteractionType.ping:
        return {"type": InteractionResponseType.pong}

    if req_type == InteractionType.application_command:
        commands = [SPTPing(), SPTStop(), SPTStart(), SPTRestart(), SPTCurrentlyPlaying()]
        is_cmd_found = False
        for cmd in commands:
            if cmd.matches(data):
                is_cmd_found = True
                cmd.apply()
                break

        if not is_cmd_found:
            print(f"Unknown command: {data}")
            raise HTTPException(status_code=400, detail='Unknown command')

    print(f"Unknown interaction type: {req_type}")
    raise HTTPException(status_code=400, detail='Unknown interaction type')
