import logging

logger = logging.getLogger('LogEmperor')


def init(log_level):
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(getattr(logging, log_level))
