import collections
import json

from AppConfig import appConfig
from Client import Client
from GameHost import GameHost


class AppServer:

    def __init__(self):
        self.CLIENTS = collections.defaultdict(Client)
        self.host: GameHost = GameHost()

    async def server_handler(self, ws, path):

        client = Client(ws)

        self.CLIENTS[client.connectionId] = ws

        await client.OnWsConnected()

        try:
            async for msg in ws:
                try:
                    jsonData = json.loads(msg)

                    await client.OnWsReceived(jsonData)

                except KeyError:
                    appConfig.log.debug("Json from %s is not valid : %s", client.connectionId, msg)

                except ValueError:
                    appConfig.log.debug("Message from %s is not valid json string : %s", client.connectionId, msg)

        finally:
            await client.OnWsDisconnected()

            await ws.close()

            self.CLIENTS.pop(client.connectionId)

            appConfig.log.debug('disconnect %s', client.connectionId)

        return ws


appServer = AppServer()
