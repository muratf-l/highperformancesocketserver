from enum import Enum


class Action(Enum):
    Error = 10
    UserInfo = 7
    ConnectionOK = 8
    GameJoin = 4
    GameLeave = 5
    GameUserList = 6


class UserRegisterStatus(Enum):
    Guest = 0
    Registered = 10


class UserOnlineStatus(Enum):
    Offline = 0
    Online = 10


class UserRegisterMethod(Enum):
    Unknow = 0
    Mail = 10
    Facebook = 20


class ResponseCode(Enum):
    OK = 200
    Error = 500


class GameStatus(Enum):
    Unknow = 0
    Waiting = 10
    Closing = 20
    Closed = 20
    Running = 30
