import json

from Client import Client
from Enums import UserOnlineStatus, Action
from models.GamePlayerInfo import GamePlayerInfo


class GamePlayer():

    def __init__(self, client: Client, game_id: str, index: int):
        self.index = index
        self.status: UserOnlineStatus = UserOnlineStatus.Online

        self.client = client
        self.client.setGame(game_id)

    async def sendGameJoinMessage(self):
        await self.client.sendMessage({"action": Action.GameJoin.value, "game": self.getGameId()})

    async def sendGameLeaveMessage(self):
        await self.client.sendMessage({"action": Action.GameLeave.value, "game": self.getGameId()})

    async def sendMessage(self, msg: json):
        await self.client.sendMessage(msg)

    def getPlayerInfo(self):
        info = GamePlayerInfo()
        info.index = self.index
        info.picture = self.client.userInfo.picture
        info.name = self.client.userInfo.name
        info.status = self.status.value
        return info.__dict__

    def getGameId(self):
        return self.client.getGameId()

    def getClientToken(self):
        return self.client.getClientToken()
