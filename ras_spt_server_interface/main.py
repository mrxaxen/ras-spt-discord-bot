# TODO: Only allow request handling from the bot as origin(based on ip/domain)
import subprocess
import os
import uvicorn

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

RAS_SPT_SERVER_SERVICE_NAME = os.getenv('RAS_SPT_SERVER_SERVICE_NAME')
RAS_SPT_SERVER_HOST = os.getenv('RAS_SPT_SERVER_HOST')
RAS_SPT_SERVER_PORT = os.getenv('RAS_SPT_SERVER_PORT')

CMD_SERVER_OPS = {
    'spt-server-start': 'start',
    'spt-server-stop': 'stop',
    'spt-server-restart': 'restart',
}

app = FastAPI()


@app.post('/spt_server/{server_op_param}')
async def server_start(server_op_param: str):
    if RAS_SPT_SERVER_SERVICE_NAME is None:
        raise HTTPException(status_code=503, detail='Service name not defined.')

    try:
        server_op = CMD_SERVER_OPS[server_op_param]
        cmd = f'nssm {server_op} {RAS_SPT_SERVER_SERVICE_NAME}'.split()
        process = subprocess.run(cmd)
    except KeyError:
        # TODO: LOG
        print(f'No such operation found for the spt-server service: {server_op_param}')


def main():
    if RAS_SPT_SERVER_HOST is None or RAS_SPT_SERVER_PORT is None:
        raise Exception('Server host or port is not defined! Exiting.')

    uvicorn.run(app=app, host=RAS_SPT_SERVER_HOST, port=int(RAS_SPT_SERVER_PORT))


if __name__ == '__main__':
    main()
