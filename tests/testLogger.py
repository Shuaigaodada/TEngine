import env
from TEngine import DebugLogger

logger = DebugLogger("/workspaces/TEngine/logs/test.log")
logger.Info("Hello World")
logger.Error("Hello World")
logger.Warning("Hello World")
