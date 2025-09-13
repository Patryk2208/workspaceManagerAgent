import logging
import asyncio
import concurrent.futures
import time
from asyncio import TaskGroup, CancelledError
from typing import Optional

from model.api.rest_client import HTTPClient
from model.config import config

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        #agent params
        self.interval = config.poll_interval

        #synchronization and concurrency
        self.stop_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()
        self.task_group : Optional[TaskGroup] = None
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="model_thread")

        #orchestrated agent tools
        self.api_client = HTTPClient(config.server_url, config.request_timeout)
        self.model = None


    async def run_agent(self):
        """
        main function of the agent, starts the agent thread, interacts with the user, collecting performance data.
        """
        try:
            async with asyncio.TaskGroup() as self.task_group:
                self.task_group.create_task(self.cancellation_task())
                self.task_group.create_task(self.run_refinement_iterations())
                while True:
                    pass
                    #todo agent procedures
        except asyncio.CancelledError:
            logger.debug("agent cancelled")


    async def run_refinement_iterations(self):
        """
        main loop of the refinement algorithm, gets state updates, runs them through the model, posts verified commands back to the server.
        """
        try:
            async with self.api_client:
                while True:
                    state = await self.task_group.create_task(self.api_client.get_state())
                    #todo fp on nn
                    #todo post command
        except asyncio.CancelledError:
            logger.debug("refinement iterations cancelled")


    async def cancellation_task(self):
        await self.stop_event.wait()
        raise asyncio.CancelledError


    def stop_agent(self):
        self.stop_event.set()
        #todo agent stopping procedure
