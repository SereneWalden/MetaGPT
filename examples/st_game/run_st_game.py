#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : entry of Stanford Town(ST/st) game

import asyncio
import fire
import datetime

from examples.st_game.maze_environment import MazeEnvironment
from examples.st_game.stanford_town import StanfordTown
from examples.st_game.roles.st_role import STRole
from examples.st_game.utils.mg_ga_transform import get_reverie_meta, write_curr_sim_code, write_curr_step
from examples.st_game.utils.const import STORAGE_PATH
from examples.st_game.utils.utils import copy_folder


async def startup(idea: str,
                  fork_sim_code: str,
                  sim_code: str,
                  investment: float = 30.0,
                  n_round: int = 500):
    # copy `storage/{fork_sim_code}` to `storage/{sim_code}`
    copy_folder(str(STORAGE_PATH.joinpath(fork_sim_code)), str(STORAGE_PATH.joinpath(sim_code)))

    # get role names from `storage/{simulation_name}/reverie/meta.json` and then init roles
    reverie_meta = get_reverie_meta(fork_sim_code)
    roles = []
    sim_path = STORAGE_PATH.joinpath(sim_code)
    sim_path.mkdir(exist_ok=True)
    for idx, role_name in enumerate(reverie_meta["persona_names"]):
        role_stg_path = STORAGE_PATH.joinpath(fork_sim_code).joinpath(f"personas/{role_name}")
        has_inner_voice = True if idx == 0 else False
        role = STRole(name=role_name,
                      sim_code=sim_code,
                      profile=f"STMember_{idx}",
                      step=reverie_meta.get("step", 0),
                      start_date=reverie_meta.get("start_date"),
                      curr_time=reverie_meta.get("curr_time"),
                      sec_per_step=reverie_meta.get("sec_per_step"),
                      has_inner_voice=has_inner_voice)
        role.load_from(role_stg_path)
        roles.append(role)

    # init temp_storage
    write_curr_sim_code({"sim_code": sim_code})
    write_curr_step({"step": reverie_meta.get("step", 0)})

    town = StanfordTown(sim_path=sim_path, 
                        environment=MazeEnvironment(
                            time_delta=datetime.timedelta(seconds = reverie_meta.get("sec_per_step")),
                            curr_time=datetime.datetime.strptime(reverie_meta.get("curr_time"), "%B %d, %Y, %H:%M:%S")
                        ))
    town.wakeup_roles(roles)

    town.invest(investment)
    town.start_project(idea)

    await town.run(n_round)


def main(idea: str,
         fork_sim_code: str,
         sim_code: str,
         investment: float = 30.0,
         n_round: int = 500):
    """
    Args:
        idea: idea works as an `inner voice` to the first agent.
        fork_sim_code: old simulation name to start with
        sim_code: new simulation name to save simulation result
        investment: the investment of running agents
        n_round: rounds to run agents
    """

    asyncio.run(startup(idea=idea,
                        fork_sim_code=fork_sim_code,
                        sim_code=sim_code,
                        investment=investment,
                        n_round=n_round))


if __name__ == "__main__":
    fire.Fire(main)
