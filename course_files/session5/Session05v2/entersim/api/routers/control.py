from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Union, Literal, Optional, Any
from pprint import pprint
from entersim.sim.control import Simulation
from entersim.sim.enterprise import Time, SimulationState
from fastapi_utils.inferring_router import InferringRouter
import entersim.sim.examples.enterprise_example1 as ex1
import entersim.sim.examples.enterprise_example2 as ex2
import entersim.sim.examples.enterprise_example3 as ex3
from copy import deepcopy

router = InferringRouter(prefix="/control")

sim: Optional[Simulation] = None


def checked_sim() -> Simulation:
    if sim is not None:
        return sim
    else:
        raise HTTPException(status_code=404, detail="Simulation not already created")


class Message(BaseModel):
    message: str


def make_checked_sim_responses(http_404_error_description: str="Simulation not already created") -> Dict[Union[int, str], Dict[str, Any]]:
    return {
        404: {"model": Message, "description": http_404_error_description},
    }


@router.get("/poll/time")
def time() -> Time:
    return checked_sim().current_state.time


@router.get("/poll/sim_state")
def sim_state() -> Optional[SimulationState]:
    return checked_sim().current_state


@router.post("/poll/create_from_example/{sim_id}", status_code=201)
def create(sim_id: Literal["sim1", "sim2", "sim3"]) -> None:
    global sim
    if sim_id == "sim1":
        sim = deepcopy(ex1.sim)
    elif sim_id == "sim2":
        sim = deepcopy(ex2.sim)
    elif sim_id == "sim3":
        sim = deepcopy(ex3.sim)
    else:
        raise HTTPException(status_code=404, detail="No such sim_id example found")


@router.post("/poll/run_one_step", status_code=200)
def run_one_step() -> None:
    checked_sim().run_one_step()


routers = [router]
