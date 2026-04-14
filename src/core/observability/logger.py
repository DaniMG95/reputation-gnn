from logging import config, getLogger, INFO

class Logger:
    APP_NAME = ""

    def __init__(self, name: str):
        self.logger = getLogger(self.APP_NAME + '.' + name)

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    @classmethod
    def setup_logging(cls, app_name: str, default_level=INFO):
        cls.APP_NAME = app_name
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': default_level,
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout',
                }
            },
            'loggers': {
                cls.APP_NAME: {
                    'handlers': ['console'],
                    'level': default_level,
                    'propagate': False,
                },
                'neo4j': {
                    'handlers': ['console'],
                    'level': 'ERROR',
                    'propagate': False,
                },
            }
        }

        config.dictConfig(logging_config)