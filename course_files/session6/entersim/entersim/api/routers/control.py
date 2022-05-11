from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict, Union, Literal, Optional, Any
from pprint import pprint
from entersim.sim.control import Simulation
from entersim.sim.enterprise import Time, SimulationState
from fastapi_utils.inferring_router import InferringRouter
import entersim.sim.examples.enterprise_example1 as ex1
import entersim.sim.examples.enterprise_example2 as ex2
import entersim.sim.examples.enterprise_example3 as ex3
import entersim.sim.examples.enterprise_example4 as ex4
from copy import deepcopy

router = InferringRouter(prefix="/control")

sim: Optional[Simulation] = None

sim_name: str = ""


def checked_sim() -> Simulation:
    if sim is not None:
        return sim
    else:
        raise HTTPException(status_code=404, detail="Simulation not already created")


def get_sim_name() -> str:
    return sim_name


class Message(BaseModel):
    message: str


def make_checked_sim_responses(http_404_error_description: str = "Simulation not already created") -> Dict[Union[int, str], Dict[str, Any]]:
    return {
        404: {"model": Message, "description": http_404_error_description},
    }


def make_checked_sim_and_validation_error_responses(http_404_error_description: str = "Simulation not already created", http_422_error_description: str = "Validation error") -> Dict[Union[int, str], Dict[str, Any]]:
    return {
        404: {"model": Message, "description": http_404_error_description},
        422: {"model": Message, "description": http_422_error_description},
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
    global sim_name
    if sim_id == "sim1":
        sim = deepcopy(ex1.sim)
        sim_name = sim_id
    elif sim_id == "sim2":
        sim = deepcopy(ex2.sim)
        sim_name = sim_id
    elif sim_id == "sim3":
        sim = deepcopy(ex3.sim)
        sim_name = sim_id
    else:
        raise HTTPException(status_code=404, detail="No such sim_id example found")


@router.post("/poll/create_from_example_sim4/{team}", status_code=201)
def create_sim4(team: Literal["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12", "Example"]) -> None:
    global sim
    global sim_name
    sim = deepcopy(ex4.make_sim(team))
    sim_name = "sim4"


@router.post("/poll/run_one_step", status_code=200)
def run_one_step() -> None:
    checked_sim().run_one_step()


routers = [router]
