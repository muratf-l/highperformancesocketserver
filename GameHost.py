import asyncio
import collections
from asyncio import Lock

from AppConfig import appConfig
from Client import Client
from Enums import GameStatus
from Game import Game


class GameHost:
    def __init__(self):
        self.lock = Lock()
        self.runningGames = collections.defaultdict(Game)

    async def GameFindOrCreate(self, client: Client, capacity: int):
        async with self.lock:
            game = None

            for live_game in self.runningGames.values():
                if live_game.gameStatus == GameStatus.Waiting and \
                        not live_game.IsFull() and \
                        not live_game.IsPlayerInGame(client.getClientToken()):
                    game = live_game
                    break

            if game is None:
                game = await self.GameCreate(capacity)

            await game.PlayerAdd(client)

            # appConfig.log.debug("player add g:%s c:%s", game.gameId, client.userInfo.token)

            return

    async def GameLeft(self, client: Client):
        async with self.lock:
            if client.getGameId() is None or \
                    client.userInfo is None or \
                    not client.getGameId() in self.runningGames.keys():
                client.setGame(None)
                return

            game = self.runningGames[client.getGameId()]

            await game.PlayerRemove(client)

            return

    async def GameCreate(self, capacity: int):
        game = Game()

        await game.AttemptSetup(capacity)

        self.runningGames[game.gameId] = game

        return game

    async def GameCheckLoop(self):
        gameControlTimeOut: int = appConfig.config["GameControlLoopSeconds"]

        while True:
            closeGameCount: int = 0

            for key, live_game in list(self.runningGames.items()):
                if live_game.gameStatus == GameStatus.Closed:
                    closeGameCount += 1
                    self.runningGames.pop(key)

            appConfig.log.debug("online game:%i close game:%i", len(self.runningGames), closeGameCount)
            await asyncio.sleep(gameControlTimeOut)
