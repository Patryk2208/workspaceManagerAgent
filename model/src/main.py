import asyncio
import logging
import time
from model.agent.program_loop import Agent

logger = logging.getLogger(__name__)

async def main():
    agent = Agent()
    asyncio.create_task(agent.run_agent())
    logger.debug("main sleeping for 10 seconds...")
    await asyncio.sleep(10)
    agent.stop_agent()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())