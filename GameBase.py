import collections
import json
from abc import abstractmethod, ABC
from asyncio import Lock

from Client import Client
from Enums import UserOnlineStatus, Action, GameStatus
from GamePlayer import GamePlayer
from Utils import getId


class GameBase(ABC):

    def __init__(self):
        self.lock = Lock()
        self.gameId = getId()
        self.gameCapacity: int = 0
        self.gamePlayers = collections.defaultdict(GamePlayer)
        self.gameStatus: GameStatus = GameStatus.Unknow

    @abstractmethod
    def GameStarted(self):
        pass

    @abstractmethod
    def GameClosed(self):
        pass

    @abstractmethod
    def PlayerJoined(self, player: GamePlayer):
        pass

    @abstractmethod
    def PlayerLeft(self, player: GamePlayer):
        pass

    def setStatus(self, status: GameStatus):

        if status == GameStatus.Running:
            self.GameStarted()

        elif status == GameStatus.Closing:
            self.GameClosed()
            self.gamePlayers.clear()
            status = GameStatus.Closed

        self.gameStatus = status

    async def PlayerAdd(self, client: Client):
        if self.gameStatus != GameStatus.Waiting:
            return

        async with self.lock:
            if not self.IsFull():
                player = GamePlayer(client, self.gameId, len(self.gamePlayers))

                await player.sendGameJoinMessage()

                self.gamePlayers[player.getClientToken()] = player

                await self.sendGamePlayerList()

                self.PlayerJoined(player)

                if self.IsFull() and self.gameStatus == GameStatus.Waiting:
                    self.setStatus(GameStatus.Running)

                return

    async def PlayerRemove(self, client: Client):
        async with self.lock:
            if client.getClientToken() in self.gamePlayers.keys():
                player: GamePlayer = self.gamePlayers[client.getClientToken()]

                player.status = UserOnlineStatus.Offline

                client.setGame(None)

                await player.sendGameLeaveMessage()

                await self.sendGamePlayerList()

                self.PlayerLeft(player)

                if self.IsEmpty():
                    self.setStatus(GameStatus.Closing)

                return

    def IsEmpty(self):
        if len(self.gamePlayers) == 0:
            return True

        count: int = 0

        for player in self.gamePlayers.values():
            if player.status == UserOnlineStatus.Offline:
                count += 1

        if count >= len(self.gamePlayers):
            return True

        return False

    def IsFull(self):
        if len(self.gamePlayers) >= self.gameCapacity:
            return True
        else:
            return False

    def IsPlayerInGame(self, playerId: str):
        if playerId in self.gamePlayers.keys():
            return True

        return False

    async def AttemptSetup(self, capacity: int):
        self.gameCapacity = capacity
        self.setStatus(GameStatus.Waiting)

    async def sendGamePlayerList(self):
        player_list = []

        for player in self.gamePlayers.values():
            player_list.append(player.getPlayerInfo())

        await self.BroadcastMessage({"action": Action.GameUserList.value, "game": self.gameId, "data": player_list})

    async def BroadcastMessage(self, msg: json):
        for player in self.gamePlayers.values():
            if player.status == UserOnlineStatus.Online:
                await player.sendMessage(msg)
