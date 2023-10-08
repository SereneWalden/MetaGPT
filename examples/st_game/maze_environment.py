#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : maze environment
import asyncio
from pydantic import Field
import datetime
from metagpt.environment import Environment
from metagpt.roles.role import Role

from examples.st_game.maze import Maze


class MazeEnvironment(Environment):

    maze: Maze = Field(default_factory=Maze)
    step: int = Field(default=0)
    time_delta: datetime.timedelta = Field(default=datetime.timedelta(seconds=20))
    curr_time: datetime.datetime = Field(default=datetime.datetime(2023,2,13,0,0,0))

    def add_role(self, role: Role):
        role.set_env(self)
        self.roles[role.name] = role  # use role.name as key not role.profile

    async def run(self, k=1):
        """处理一次所有信息的运行
        Process all Role runs at once
        """
        # while not self.message_queue.empty():
        # message = self.message_queue.get()
        # rsp = await self.manager.handle(message, self)
        # self.message_queue.put(rsp)
        for _ in range(k):
            futures = []
            for role in self.roles.values():
                future = role.run()
                futures.append(future)
            await asyncio.gather(*futures)
            self.step += 1
            self.curr_time += self.time_delta
