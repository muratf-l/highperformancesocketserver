import json

from sqlalchemy.orm import sessionmaker

from Enums import UserRegisterStatus, UserRegisterMethod, UserOnlineStatus, ResponseCode
from Utils import getId
from models.UserInfo import UserInfo


class Database:

    def __init__(self):
        self.models = {}

        from models.User import User
        self.models["User"] = User
        pass

    def createDatabase(self):
        from AppConfig import appConfig
        from sqlalchemy import create_engine
        self.engine = create_engine(appConfig.config['ConnectionString'], echo=appConfig.isDebug)

        from AppStartup import Base
        # Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        self.session = sessionmaker(bind=self.engine)

    async def registerUserFromFacebook(self, data: json, cb):
        from models.User import User

        session = self.session()

        query = session.query(User).filter(User.PlatformId == data["id"]).limit(1).all()

        queryCount = len(query)

        if queryCount > 0:
            user = query[0]
            await self.getUserInfoFromRecord(user, cb)
            return

        user = User()
        user.UserToken = getId()
        user.PlatformId = data["id"]
        user.NameFirst = data["name"]
        user.ProfileImageUrl = data["photo"]
        user.Locale = data["locale"]
        user.PlatformMethod = data["platform"]
        user.RegisterStatus = UserRegisterStatus.Registered.value
        user.OnlineStatus = UserOnlineStatus.Online.value
        user.RegisterMethod = UserRegisterMethod.Facebook.value

        session.add(user)
        session.commit()
        await self.getUserInfoFromRecord(user, cb)

    async def registerUserFromMail(self, data: json, cb):
        from models.User import User

        session = self.session()

        queryCount = session.query(User).filter(User.Email == data["mail"]).limit(1).count()

        if queryCount > 0:
            await cb(ResponseCode.Error.value, None, "already exists")
            return

        user = User()
        user.UserToken = getId()
        user.NameFirst = data["name"]
        user.Email = data["mail"]
        user.Password = data["pass"]
        user.RegisterStatus = UserRegisterStatus.Registered.value
        user.OnlineStatus = UserOnlineStatus.Online.value
        user.RegisterMethod = UserRegisterMethod.Mail.value

        session.add(user)
        session.commit()
        await self.getUserInfoFromRecord(user, cb)

    async def loginUserFromMailPassword(self, data: json, cb):
        from models.User import User

        session = self.session()

        query = session.query(User).filter(User.Email == data["mail"] and User.Password == data["pass"]).limit(1).all()

        queryCount = len(query)

        if queryCount > 0:
            user = query[0]
            await self.getUserInfoFromRecord(user, cb)
            return

        await cb(ResponseCode.Error.value, None, "not found")

    async def getUserInfoFromRecord(self, user, cb):
        userInfo = UserInfo()
        userInfo.token = user.UserToken
        userInfo.coin = 2500
        userInfo.name = user.NameFirst
        userInfo.picture = user.ProfileImageUrl

        await cb(ResponseCode.OK.value, userInfo, None)

    async def setUserOnlineStatus(self, userInfo: UserInfo, status: UserOnlineStatus):
        from models.User import User

        session = self.session()

        session.query(User).filter(User.UserToken == userInfo.token) \
            .update({User.OnlineStatus: status.value},
                    synchronize_session=False)

        session.commit()


database = Database()
