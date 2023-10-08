#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : StanfordTown to works like SoftwareCompany
import json
from pydantic import Field
from pathlib import Path
from metagpt.software_company import SoftwareCompany
# from metagpt.roles.role import Role
from metagpt.schema import Message
from metagpt.logs import logger

from examples.st_game.roles.st_role import STRole
from examples.st_game.maze_environment import MazeEnvironment
from examples.st_game.actions.user_requirement import UserRequirement


class StanfordTown(SoftwareCompany):

    environment: MazeEnvironment = Field(default_factory=MazeEnvironment)
    sim_path: Path

    def wakeup_roles(self, roles: list[STRole]):
        logger.warning(f"The Town add {len(roles)} roles, and start to operate.")
        self.environment.add_roles(roles)

    def start_project(self, idea):
        self.environment.publish_message(
            Message(role="User", content=idea, cause_by=UserRequirement)
        )

    def save(self):
        role_locations = {}
        role_movements = {}
        for role_name, role in self.environment.roles.items():
            role_path = self.sim_path.joinpath(f"personas\{role_name}")
            role.save_into(role_path)
            role_locations[role_name] = {
                "maze": role.maze.name,
                "x": role.role_tile[0],
                "y": role.role_tile[1]
            }

        env_path = self.sim_path.joinpath(f"environment\{self.environment.step}.json")
        with open(str(env_path), "w") as f:
            json.dump(role_locations)

        movement_dict = {
            "personas": role_movements,
            "meta": {"curr_time": self.environment.curr_time}
        }
        movement_path = self.sim_path.joinpath(f"movement\{self.environment.step}.json")
        with open(str(movement_path), "w") as f:
            json.dump(movement_dict, movement_path)
        
    async def run(self, n_round=3):
        """Run company until target round or no money"""
        while n_round > 0:
            self.save()
            n_round -= 1
            logger.debug(f"{n_round=}")
            self._check_balance()
            await self.environment.run()
        return self.environment.history
    