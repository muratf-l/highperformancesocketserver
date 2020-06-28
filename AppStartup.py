import asyncio
import ssl
import sys
import logging

import websockets
from sqlalchemy.ext.declarative import declarative_base

from AppConfig import appConfig
from AppServer import appServer

Base = declarative_base()

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        logging.critical('Invalid Args (dev,pro)')
        sys.exit()

    appConfig.load(args[1])
    appConfig.log.debug('start server %s' % str(appConfig.config['Port']))

    from Database import database

    database.createDatabase()

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    event_loop = asyncio.get_event_loop()
    event_loop.set_debug(appConfig.isDebug)

    GameLoop = asyncio.get_event_loop().create_task(appServer.host.GameCheckLoop())

    if not appConfig.isDebug:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain('public.crt', 'private.key')
        start_server = websockets.serve(appServer.server_handler, '0.0.0.0', appConfig.config['Port'], ssl=ssl_context)
    else:
        start_server = websockets.serve(appServer.server_handler, '0.0.0.0', appConfig.config['Port'])

    event_loop.run_until_complete(start_server)

    try:
        event_loop.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        GameLoop.cancel()
        pass

    event_loop.close()

    appConfig.log.debug('Stop server')
