from pprint import pformat

import logging
from tradingagents.log.log import TRADING_AGENTS_GRAPH
tag_logger = logging.getLogger(TRADING_AGENTS_GRAPH)


def is_empty(obj):
    return obj is None or len(obj) <= 0


def _get_log_method(log_level):
    if log_level == logging.INFO:
        return tag_logger.info 
    elif log_level == logging.WARNING:
        return tag_logger.warning
    elif log_level == logging.ERROR:
        return tag_logger.error
    elif log_level == logging.FATAL:
        return tag_logger.fatal
    else:
        return tag_logger.debug


def pretty_log(data, log_level=logging.INFO):
    if is_empty(data):
        return
    
    log_method = _get_log_method(log_level)

    formatted = pformat(data)
    for line in formatted.splitlines():
        log_method(line)


def log(data, log_level=logging.INFO):
    if is_empty(data):
        return
    
    log_method = _get_log_method(log_level)
    log_method(data)
        