import logging
import asyncio
import concurrent.futures
from asyncio import TaskGroup
from typing import Optional

from model.agent.performance_data import PerformanceData
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
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="model_thread")

        #orchestrated agent tools
        self.performance_data : PerformanceData = PerformanceData()
        self.api_client : HTTPClient = HTTPClient(config.server_url, config.request_timeout)
        self.model = None


    async def run_agent(self):
        """
        main function of the agent, interacts with the user, collects performance data.
        runs the refinement algorithm, gets state updates, runs them through the model,
        posts verified commands back to the server.
        """
        try:
            async with asyncio.TaskGroup() as self.task_group:
                self.task_group.create_task(self.cancellation_task())
                async with self.api_client:
                    while True:
                        state = await self.task_group.create_task(self.api_client.get_state())
                        @self.performance_data.measure_model_iteration_performance
                        async def model_predict():
                            return await asyncio.sleep(2)
                        # todo fp on nn (after model implementation)
                        
                        # todo post command
        except asyncio.CancelledError:
            logger.debug("agent cancelled")


    async def cancellation_task(self):
        await self.stop_event.wait()
        raise asyncio.CancelledError


    def stop_agent(self):
        self.stop_event.set()
        #todo agent stopping procedure
