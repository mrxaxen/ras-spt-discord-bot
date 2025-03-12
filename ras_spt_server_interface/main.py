# TODO: Only allow request handling from the bot as origin(based on ip/domain)
import subprocess
import os

from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

SPT_SERVER_SERVICE_NAME = os.getenv('SPT_SERVER_SERVICE_NAME')
app = FastAPI()


def check_service_name_defined():
    if SPT_SERVER_SERVICE_NAME is None:
        raise Exception('Service name not defined.')


@app.post('/server/start')
async def server_start(req: Request):
    check_service_name_defined()
    cmd = f'nssm start {SPT_SERVER_SERVICE_NAME}'.split()

    process = subprocess.run(cmd)  # TODO: Either do an async await somehow, or use POpen


@app.post('/server/stop')
async def server_stop(req: Request):
    check_service_name_defined()
    cmd = f'nssm stop {SPT_SERVER_SERVICE_NAME}'.split()
    process = subprocess.run(cmd)


@app.post('/server/restart')
async def server_restart(req: Request):
    check_service_name_defined()
    pass
