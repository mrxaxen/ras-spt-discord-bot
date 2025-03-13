# TODO: Only allow request handling from the bot as origin(based on ip/domain)
import subprocess
import os
import uvicorn
import sys

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.trustedhost import TrustedHostMiddleware

load_dotenv()

RAS_SPT_SERVER_SERVICE_NAME = os.getenv('RAS_SPT_SERVER_SERVICE_NAME')
RAS_SPT_SERVER_HOST = os.getenv('RAS_SPT_SERVER_HOST')
RAS_SPT_SERVER_PORT = os.getenv('RAS_SPT_SERVER_PORT')
RAS_SPT_TRUSTED_HOST = os.getenv('RAS_SPT_TRUSTED_HOST')

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
        print(f'Command to execute: {cmd}')
        process = subprocess.run(cmd, capture_output=True)
        print(
            f'Service returned: {process.stdout.decode(sys.stdout.encoding)}\n{process.stderr.decode(sys.stdout.encoding)}')
    except KeyError:
        # TODO: LOG
        print(f'No such operation found for the spt-server service: {server_op_param}')


def main():
    mandatory_env_vars = [
        RAS_SPT_SERVER_HOST,
        RAS_SPT_SERVER_PORT,
        RAS_SPT_TRUSTED_HOST,
    ]

    if not all(mandatory_env_vars):
        raise Exception('Server host or port is not defined! Exiting.')

    app.add_middleware(TrustedHostMiddleware, [RAS_SPT_TRUSTED_HOST])
    uvicorn.run(app=app, host=RAS_SPT_SERVER_HOST, port=int(RAS_SPT_SERVER_PORT))


if __name__ == '__main__':
    main()
