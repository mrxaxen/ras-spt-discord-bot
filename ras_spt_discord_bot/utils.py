import random
import traceback
from typing import Any

from pydantic import TypeAdapter
import conf

from python_on_whales import docker
from models import ServerTwoPartResponse


def __read_server_starting_responses():
    with open('responses/server_starting.json', 'r') as file:
        adapter = TypeAdapter(list[ServerTwoPartResponse])
        return adapter.validate_strings(file)


def __read_server_restarting_responses():
    with open('responses/server_restarting.json', 'r') as file:
        adapter = TypeAdapter(list[ServerTwoPartResponse])
        return adapter.validate_strings(file)


def __read_server_stopping_responses():
    with open('responses/server_stopping.json', 'r') as file:
        adapter = TypeAdapter(list[ServerTwoPartResponse])
        return adapter.validate_strings(file)


def __read_server_already_stopped_responses():
    with open('responses/server_already_stopped', 'r') as file:
        return file.read().split('\n')


def __read_server_ping_dedicated_online_responses():
    with open('responses/server_ping_dedicated_online', 'r') as file:
        return file.read().split('\n')


def __read_server_ping_dedicated_offline_responses():
    with open('responses/server_ping_dedicated_offline', 'r') as file:
        return file.read().split('\n')


def __read_server_ping_dedicated_restarting_responses():
    with open('responses/server_ping_dedicated_restarting', 'r') as file:
        return file.read().split('\n')


def __read_server_ping_headless_online_responses():
    with open('responses/server_ping_headless_online', 'r') as file:
        return file.read().split('\n')


def __read_server_ping_headless_offline_responses():
    with open('responses/server_ping_headless_offline', 'r') as file:
        return file.read().split('\n')


def __read_server_ping_headless_restarting_responses():
    with open('responses/server_ping_headless_restarting', 'r') as file:
        return file.read().split('\n')


server_already_stopped_responses = __read_server_already_stopped_responses()
server_starting_responses = __read_server_starting_responses()
server_stopping_responses = __read_server_stopping_responses()
server_restarting_responses = __read_server_restarting_responses()
server_ping_dedicated_online_responses = __read_server_ping_dedicated_online_responses()
server_ping_dedicated_offline_responses = __read_server_ping_dedicated_offline_responses()
server_ping_dedicated_restarting_responses = __read_server_ping_dedicated_restarting_responses()
server_ping_headless_online_responses = __read_server_ping_headless_online_responses()
server_ping_headless_offline_responses = __read_server_ping_headless_offline_responses()
server_ping_headless_restarting_responses = __read_server_ping_headless_restarting_responses()


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
        'name': conf.RAS_SPT_HEADLESS_CONTAINER_NAME
    }
    headless_container = None
    try:
        headless_container = docker.ps(True, filters=filters)[0]  # type: ignore
    except IndexError:
        print('Container is not present.')
    except Exception:
        traceback.print_exc()

    return headless_container
