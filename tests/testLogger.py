import env
from TEngine import DebugLogger

logger = DebugLogger("/workspaces/TEngine/logs/test.log")
logger.info("Hello World")
logger.error("Hello World")
logger.warning("Hello World")
