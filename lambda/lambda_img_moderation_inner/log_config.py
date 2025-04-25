import logging
import logging.config


def setup_logging():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                # 'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                'format': '%(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',  # Default is stderr
            }
            # ,
            # 'file': {
            #     'level': 'DEBUG',
            #     'formatter': 'standard',
            #     'class': 'logging.FileHandler',
            #     'filename': 'debug.log',
            #     'mode': 'a',
            # },
        },
        'loggers': {
            '': {  # root logger
                # 'handlers': ['default', 'file'],
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    logging.config.dictConfig(logging_config)



def get_logger(name):
    logger = logging.getLogger(name)
    if name.startswith('sensitive_module'):
        logger.setLevel(logging.WARNING)
    return logger


if __name__ == '__main__':
    setup_logging()
    logger = get_logger(__name__)
    logger.info("hello")
    logger.error("error")
