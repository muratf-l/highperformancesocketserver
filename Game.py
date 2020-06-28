from GameBase import GameBase
from GamePlayer import GamePlayer


class Game(GameBase):

    def GameStarted(self):
        pass

    def GameClosed(self):
        pass

    def PlayerJoined(self, player: GamePlayer):
        pass

    def PlayerLeft(self, player: GamePlayer):
        pass
