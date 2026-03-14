import os
import logging
from logging.handlers import RotatingFileHandler


tag_logger = logging.getLogger("TradingAgentsGraph")
tag_logger.setLevel(logging.DEBUG)

tag_log_dir = os.path.join("output", "logs", "trading_agents_graph")
os.makedirs(tag_log_dir, exist_ok=True)

tag_logger_handler = RotatingFileHandler(os.path.join(tag_log_dir, "trading_agents_graph.log"), maxBytes=20 * 1024 * 1024, backupCount=10)
tag_logger_handler.setLevel(logging.INFO)
tag_logger_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
tag_logger_handler.setFormatter(tag_logger_formatter)

tag_logger.addHandler(tag_logger_handler)
