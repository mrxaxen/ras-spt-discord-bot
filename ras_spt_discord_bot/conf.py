import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

CMD_PING_SPT_SERVER = "spt-ping"
CMD_STOP_SPT_SERVER = "spt-dedicated-stop"
CMD_START_SPT_SERVER = "spt-dedicated-start"
CMD_RESTART_SPT_SERVER = "spt-dedicated-restart"
CMD_START_SPT_HEADLESS = "spt-headless-start"
CMD_RESTART_SPT_HEADLESS = "spt-headless-restart"
CMD_STOP_SPT_HEADLESS = "spt-headless-stop"
CMD_CURRENTLY_PLAYING = "spt-playing"
CMD_SERVER_HELLO = "spt-hello"

RAS_SPT_WEBSERVER_URL_PING = os.getenv('RAS_SPT_WEBSERVER_URL_PING')
RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING = os.getenv('RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING')
RAS_SPT_SERVER_INTERFACE_URL_STOP = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_STOP')
RAS_SPT_SERVER_INTERFACE_URL_START = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_START')
RAS_SPT_SERVER_INTERFACE_URL_RESTART = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_RESTART')
RAS_SPT_DISCORD_EFT_ROLE_ID = int(os.getenv('RAS_SPT_DISCORD_EFT_ROLE_ID'))
RAS_SPT_HEADLESS_CONTAINER_NAME = os.getenv('RAS_SPT_HEADLESS_CONTAINER_NAME')
