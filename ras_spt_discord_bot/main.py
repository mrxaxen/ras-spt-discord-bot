import random
import httpx
import zlib
import discord
import conf
import utils as ras_utils

from python_on_whales import docker
from discord.ext import commands

bot = discord.Bot()


@bot.slash_command(name=conf.CMD_SERVER_HELLO)
async def server_hello(ctx: commands.Context):
    await ctx.channel.send('Hello!')


@bot.slash_command(name=conf.CMD_PING_SPT_SERVER)
async def ping_server(ctx: commands.Context):
    assert conf.RAS_SPT_WEBSERVER_URL_PING

    author = ctx.author
    role = discord.utils.get(ctx.guild.roles, name="EFT Player")
    conditions = [
        isinstance(author, discord.Member),
        role in ctx.author.roles
    ]
    if not all(conditions):
        return

    http_client = httpx.AsyncClient()
    response = await http_client.request(method='GET', url=conf.RAS_SPT_WEBSERVER_URL_PING)
    response.raise_for_status()

    content = zlib.decompress(response.content).decode()
    dedicated_chat_response = None
    if 'pong' in content or 'PONG' in content:
        dedicated_chat_response = random.choice(ras_utils.server_ping_dedicated_online_responses)
    else:
        dedicated_chat_response = random.choice(ras_utils.server_ping_dedicated_offline_responses)
    await ctx.channel.send(f'{ctx.author.display_name}: How is the dedicated server doing?')
    await ctx.channel.send(dedicated_chat_response)

    headless_chat_response = None
    if ras_utils.is_headless_online():
        if ras_utils.is_headless_restarting():
            headless_chat_response = random.choice(
                ras_utils.server_ping_headless_restarting_responses)
        else:
            headless_chat_response = random.choice(ras_utils.server_ping_headless_online_responses)
    else:
        headless_chat_response = random.choice(ras_utils.server_ping_headless_restarting_responses)
    await ctx.channel.send(f'{ctx.author.display_name}: What about the headless client?')
    await ctx.channel.send(headless_chat_response)


@bot.slash_command(name=conf.CMD_RESTART_SPT_HEADLESS)
async def restart_headless(ctx: commands.Context):
    await ctx.channel.send(f'{ctx.author.display_name}: Could you restart the headless client?')
    role = discord.utils.get(ctx.guild.roles, name="EFT Player")
    conditions = [
        ras_utils.is_headless_online(),
        not ras_utils.is_headless_restarting(),
        role in ctx.author.roles
    ]
    if not all(conditions):
        print('Condition not met.')
        await ctx.channel.send('Nope, no can do. Not for you at least.. You know lack of authority and such..')
        return

    assert conf.RAS_SPT_HEADLESS_CONTAINER_NAME

    container = ras_utils.get_headless_container()
    if container is not None and not ras_utils.is_headless_restarting():
        response = random.choice(ras_utils.server_restarting_responses)
        await ctx.channel.send(response.first)
        docker.restart(conf.RAS_SPT_HEADLESS_CONTAINER_NAME)  # type: ignore
        await ctx.channel.send(response.final)


@bot.slash_command(name=conf.CMD_START_SPT_HEADLESS)
async def start_headless(ctx: commands.Context):
    await ctx.channel.send(f'{ctx.author.display_name}: Could you start the headless client?')
    role = discord.utils.get(ctx.guild.roles, name="EFT Player")
    conditions = [
        not ras_utils.is_headless_online(),
        not ras_utils.is_headless_restarting(),
        role in ctx.author.roles
    ]
    if not all(conditions):
        print('Condition not met.')
        await ctx.channel.send('Nope, no can do. Not for you at least.. You know lack of authority and such..')
        return

    assert conf.RAS_SPT_HEADLESS_CONTAINER_NAME

    container = ras_utils.get_headless_container()
    if container is not None and not ras_utils.is_headless_restarting():
        response = random.choice(ras_utils.server_starting_responses)
        await ctx.channel.send(response.first)
        docker.start(conf.RAS_SPT_HEADLESS_CONTAINER_NAME)  # type: ignore
        await ctx.channel.send(response.final)


@bot.slash_command(name=conf.CMD_STOP_SPT_HEADLESS)
async def stop_headless(ctx: commands.Context):
    await ctx.channel.send(f'{ctx.author.display_name}: Could you stop the headless client?')
    role = discord.utils.get(ctx.guild.roles, name="EFT Player")
    conditions = [
        ras_utils.is_headless_online(),
        ras_utils.is_headless_restarting(),
    ]
    if not any(conditions) or role not in ctx.author.roles:
        print('Condition not met.')
        await ctx.channel.send("Nope, no can do. Not for you at least.. You know lack of authority and such.. Have you even checked if it's running or not?")
        return

    assert conf.RAS_SPT_HEADLESS_CONTAINER_NAME

    container = ras_utils.get_headless_container()
    if container is not None and not ras_utils.is_headless_restarting():
        response = random.choice(ras_utils.server_stopping_responses)
        await ctx.channel.send(response.first)
        docker.stop(conf.RAS_SPT_HEADLESS_CONTAINER_NAME)  # type: ignore
        await ctx.channel.send(response.final)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    print('Message received')
    if message.author == bot.user:
        return


def main():
    assert conf.DISCORD_TOKEN
    bot.run(conf.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
