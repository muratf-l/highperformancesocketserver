import json
import logging


class AppConfig:
    def __init__(self):
        self.config = {}
        self.isDebug = False
        self.mode = None
        self.log = logging.getLogger('app')

    def load(self, mode):
        self.mode = mode

        if mode == "dev":
            config_file = "config/config.dev.json"
        else:
            config_file = "config/config.pro.json"

        with open(config_file, 'r') as f:
            try:
                appConfig.config = json.load(f)

                ch = logging.StreamHandler()

                f = logging.Formatter('[L:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                                      datefmt='%d-%m-%Y %H:%M:%S')

                if mode == "dev":
                    self.isDebug = True
                    appConfig.log.setLevel(logging.DEBUG)
                    ch.setLevel(logging.DEBUG)
                else:
                    self.isDebug = False
                    appConfig.log.setLevel(logging.INFO)
                    ch.setLevel(logging.INFO)

                ch.setFormatter(f)

                appConfig.log.addHandler(ch)

            except Exception as e:
                appConfig.config = {}
                appConfig.log.debug("Config Load Error: %s" % e)


appConfig = AppConfig()
