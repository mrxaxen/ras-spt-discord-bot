import asyncio
import os
import traceback
import httpx
import zlib
import discord

from dotenv import load_dotenv
from python_on_whales import docker
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

CMD_PING_SPT_SERVER = "spt-ping"
CMD_STOP_SPT_SERVER = "spt-stop"
CMD_START_SPT_SERVER = "spt-start"
CMD_RESTART_SPT_SERVER = "spt-dedicated-restart"
CMD_RESTART_SPT_HEADLESS = "spt-headless-restart"
CMD_CURRENTLY_PLAYING = "spt-playing"
CMD_SERVER_HELLO = "spt-hello"

RAS_SPT_WEBSERVER_URL_PING = os.getenv('RAS_SPT_WEBSERVER_URL_PING')
RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING = os.getenv('RAS_SPT_WEBSERVER_URL_CURRENTLY_PLAYING')
RAS_SPT_SERVER_INTERFACE_URL_STOP = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_STOP')
RAS_SPT_SERVER_INTERFACE_URL_START = os.getenv('RAS_SPT_SERVER_INTERFACE_URL_START')
RAS_SPT_SERVER_INTERFACE_URL_RESTART = os.getenv('RAS_SPT_SERVER_INTERFkkjACE_URL_RESTART')
RAS_SPT_DISCORD_EFT_ROLE_ID = int(os.getenv('RAS_SPT_DISCORD_EFT_ROLE_ID'))
RAS_SPT_HEADLESS_CONTAINER_NAME = os.getenv('RAS_SPT_HEADLESS_CONTAINER_NAME')


bot = discord.Bot()


def is_headless_online() -> bool:
    headless_container = get_headless_container()
    if headless_container is None:
        return False

    conditions = [
        not headless_container.state.restarting,
        headless_container.state.running,
    ]
    return all(conditions)


def is_headless_restarting() -> bool:
    headless_container = get_headless_container()
    if headless_container is None:
        return False

    restarting = headless_container.state.restarting
    return restarting is not None and restarting


def get_headless_container():
    filters = {
        'name': RAS_SPT_HEADLESS_CONTAINER_NAME
    }
    headless_container = None
    try:
        headless_container = docker.ps(True, filters=filters)[0]  # type: ignore
    except IndexError:
        print('Container is not present.')
    except Exception:
        traceback.print_exc()

    return headless_container


@bot.slash_command(name=CMD_SERVER_HELLO)
async def server_hello(ctx: commands.Context):
    await ctx.channel.send('Hello!')


@bot.slash_command(name=CMD_PING_SPT_SERVER)
async def ping_server(ctx: commands.Context):
    assert RAS_SPT_WEBSERVER_URL_PING

    author = ctx.author
    conditions = [
        isinstance(author, discord.Member),
        author.get_role(RAS_SPT_DISCORD_EFT_ROLE_ID) is not None,  # type: ignore
    ]
    if not all(conditions):
        return

    http_client = httpx.AsyncClient()
    response = await http_client.request(method='GET', url=RAS_SPT_WEBSERVER_URL_PING)
    response.raise_for_status()

    content = zlib.decompress(response.content).decode()
    dedicated_is_online = None
    if 'pong' in content or 'PONG' in content:
        dedicated_is_online = 'online'
    else:
        dedicated_is_online = 'offline'
    await ctx.channel.send(f'RAS SPT Dedicated server is {dedicated_is_online}')

    headless_is_online = None
    if is_headless_online():
        if is_headless_restarting():
            headless_is_online = 'restarting'
        else:
            headless_is_online = 'online'
    else:
        headless_is_online = 'offline'
    await ctx.channel.send(f'RAS SPT Headless client is {headless_is_online}!')


@bot.slash_command(name=CMD_RESTART_SPT_HEADLESS)
async def restart_headless(ctx: commands.Context):
    author = ctx.author
    conditions = [
        is_headless_online(),
        is_headless_restarting(),
        isinstance(author, discord.Member),
        author.get_role(RAS_SPT_DISCORD_EFT_ROLE_ID) is not None,  # type: ignore
    ]
    if not all(conditions):
        return

    assert RAS_SPT_HEADLESS_CONTAINER_NAME
    container = get_headless_container()
    if container is not None and not is_headless_restarting():
        docker.restart(RAS_SPT_HEADLESS_CONTAINER_NAME)

    restart_success = False
    for i in range(15):
        await ctx.channel.send('Restarting headless client..')
        restart_success = docker.ps(True, filters=filters)[0].state.running  # type: ignore
        if restart_success:
            await ctx.channel.send('Server is running!')
            break
        await asyncio.sleep(5)

    if not restart_success:
        await ctx.channel.send(
            f'Server restart timed out, check status with {CMD_PING_SPT_SERVER}, and try again!')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    print('Message received')
    if message.author == bot.user:
        return


def main():
    assert DISCORD_TOKEN
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
