import asyncio
import os
import discord
import httpx
import zlib

from abc import ABC, abstractmethod
from typing import List
from dotenv import load_dotenv
from python_on_whales import docker
from python_on_whales.components.container.cli_wrapper import DockerContainerListFilters

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

CMD_PING_SPT_SERVER = "$spt-ping"
CMD_STOP_SPT_SERVER = "$spt-stop"
CMD_START_SPT_SERVER = "$spt-start"
CMD_RESTART_SPT_SERVER = "$spt-dedicated-restart"
CMD_RESTART_SPT_HEADLESS = "$spt-headless-restart"
CMD_CURRENTLY_PLAYING = "$spt-playing"
CMD_SERVER_HELLO = "$spt-hello"

RAS_SPT_WEBSERVER_URL_PING = os.getenv('RAS_SPT_WEBSERVER_URL_PING')
RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING = os.getenv('RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING')
RAS_SPT_SERVER_INTERFACE_URL_STOP = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_STOP')
RAS_SPT_SERVER_INTERFACE_URL_START = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_START')
RAS_SPT_SERVER_INTERFACE_URL_RESTART = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_RESTART')
RAS_SPT_DISCORD_EFT_ROLE_ID = int(os.getenv('RAS_SPT_DISCORD_EFT_ROLE_ID'))
RAS_SPT_HEADLESS_CONTAINER_NAME = os.getenv('RAS_SPT_HEADLESS_CONTAINER_NAME')


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


class BotCommand(ABC):

    def __init__(self, command) -> None:
        self.command = command

    async def is_headless_online(self) -> bool:
        filters = {
            'name': RAS_SPT_HEADLESS_CONTAINER_NAME
        }
        headless_container = docker.ps(True, filters=filters)[0]  # type: ignore
        conditions = [
            not headless_container.state.restarting,
            headless_container.state.running,
        ]
        return all(conditions)

    async def is_headless_restarting(self) -> bool:
        filters = {
            'name': RAS_SPT_HEADLESS_CONTAINER_NAME
        }
        headless_container = docker.ps(True, filters=filters)[0]  # type: ignore
        return headless_container.state.restarting is not None and headless_container.state.restarting

    @abstractmethod
    async def exec(self, message: discord.Message):
        raise NotImplementedError

    @abstractmethod
    async def condition(self, message: discord.Message):
        raise NotImplementedError


class ServerHelloCommand(BotCommand):

    def __init__(self, command) -> None:
        super().__init__(command=command)

    async def exec(self, message: discord.Message):
        await message.channel.send('Hello!')

    async def condition(self, message: discord.Message):
        return message.content.startswith(self.command())


class SPTPingCommand(BotCommand):

    def __init__(self, command) -> None:
        super().__init__(command=command)

    async def exec(self, message: discord.Message):
        assert RAS_SPT_WEBSERVER_URL_PING

        http_client = httpx.AsyncClient()
        response = await http_client.request(method='GET', url=RAS_SPT_WEBSERVER_URL_PING)
        response.raise_for_status()

        content = zlib.decompress(response.content).decode()
        dedicated_is_online = None
        if 'pong' in content or 'PONG' in content:
            dedicated_is_online = 'online'
        else:
            dedicated_is_online = 'offline'
        await message.channel.send(f'RAS SPT Dedicated server is {dedicated_is_online}')

        headless_is_online = None
        if self.is_headless_online():
            if self.is_headless_restarting():
                headless_is_online = 'restarting'
            else:
                headless_is_online = 'online'
        else:
            headless_is_online = 'offline'
        await message.channel.send(f'RAS SPT Headless client is {headless_is_online}!')

    async def condition(self, message: discord.Message):
        author = message.author
        conditions = [
            message.content.startswith(self.command),
            isinstance(author, discord.Member),
            author.get_role(RAS_SPT_DISCORD_EFT_ROLE_ID) is not None,  # type: ignore
        ]
        return all(conditions)


class SPTHeadlessRestartCommand(BotCommand):

    def __init__(self, command) -> None:
        super().__init__(command=command)

    async def exec(self, message: discord.Message):
        assert RAS_SPT_HEADLESS_CONTAINER_NAME
        filters = {
            'name': RAS_SPT_HEADLESS_CONTAINER_NAME
        }
        container = docker.ps(True, filters=filters)[0]  # type: ignore
        if not container.state.restarting and container.state.running:
            docker.restart(RAS_SPT_HEADLESS_CONTAINER_NAME)

        restart_success = False
        for i in range(15):
            await message.channel.send('Restarting headless client..')
            restart_success = docker.ps(True, filters=filters)[0].state.running  # type: ignore
            if restart_success:
                await message.channel.send('Server is running!')
                break
            await asyncio.sleep(5)

        if not restart_success:
            await message.channel.send(
                f'Server restart timed out, check status with {CMD_PING_SPT_SERVER}, and try again!')

    async def condition(self, message: discord.Message):
        author = message.author
        conditions = [
            self.is_headless_online(),
            self.is_headless_restarting(),
            isinstance(author, discord.Member),
            author.get_role(RAS_SPT_DISCORD_EFT_ROLE_ID) is not None,  # type: ignore
        ]
        return all(conditions)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    cmd_requests: List[BotCommand] = [
        ServerHelloCommand(CMD_SERVER_HELLO),
        SPTPingCommand(CMD_PING_SPT_SERVER),
        SPTHeadlessRestartCommand(CMD_RESTART_SPT_HEADLESS)
    ]
    if message.author == client.user:
        return


def main():
    assert DISCORD_TOKEN
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
