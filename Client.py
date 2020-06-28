import json
from asyncio import Lock

from websockets import WebSocketServerProtocol

from AppConfig import appConfig

from Enums import Action, ResponseCode, UserOnlineStatus
from Utils import getId, is_json_key_present
from models.UserInfo import UserInfo


class Client:

    def __init__(self, connection: WebSocketServerProtocol):
        self.connection: WebSocketServerProtocol = connection
        self.connectionId: str = getId()

        self.lock = Lock()
        self.gameId: str = None
        self.userInfo: UserInfo = None

    def setGame(self, gameId: str):
        self.gameId = gameId

    def getGameId(self):
        return self.gameId

    def getClientToken(self):
        return self.userInfo.token

    async def sendMessage(self, msg: json):
        if self.connection is None or self.connection.closed:
            return

        await self.connection.send(json.dumps(msg))

    async def OnWsConnected(self):
        await self.sendMessage({"action": Action.ConnectionOK.value})

    async def OnWsDisconnected(self):
        if not self.userInfo is None:
            from Database import database
            await database.setUserOnlineStatus(self.userInfo, UserOnlineStatus.Offline)

            from AppServer import appServer
            await appServer.host.GameLeft(self)

    async def OnWsReceived(self, message: json):

        try:
            action = int(message['action'])
        except:
            action = None

        if action is None:
            return

        async with self.lock:
            appConfig.log.debug('action sid:%s action:%s', self.connectionId, action)
            from Database import database

            if action == 1 and self.userInfo is None:
                if is_json_key_present(message, "data"):
                    await database.registerUserFromFacebook(message["data"], self.ActionUserInfoCallback)

            elif action == 2 and self.userInfo is None:
                if is_json_key_present(message, "data"):
                    await database.registerUserFromMail(message["data"], self.ActionUserInfoCallback)

            elif action == 3 and self.userInfo is None:
                if is_json_key_present(message, "data"):
                    await database.loginUserFromMailPassword(message["data"], self.ActionUserInfoCallback)

            elif action == 4 and not self.userInfo is None:
                if is_json_key_present(message, "data"):
                    from AppServer import appServer
                    await appServer.host.GameFindOrCreate(self, int(message["data"]["player"]))

            elif action == 5 and not self.userInfo is None:
                from AppServer import appServer
                await appServer.host.GameLeft(self)

    async def ActionUserInfoCallback(self, code: int, userInfo, message: str):
        self.userInfo = userInfo

        if code != ResponseCode.OK.value:
            await self.sendMessage({"action": code})
            return

        from Database import database
        await database.setUserOnlineStatus(self.userInfo, UserOnlineStatus.Online)
        await self.sendMessage({"action": Action.UserInfo.value, "user": self.userInfo.__dict__})
