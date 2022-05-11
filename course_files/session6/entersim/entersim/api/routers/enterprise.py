from copy import copy, deepcopy
from math import floor
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict
from pprint import pprint
from fastapi_utils.inferring_router import InferringRouter
from .control import checked_sim, make_checked_sim_and_validation_error_responses, make_checked_sim_responses, get_sim_name
from entersim.sim.enterprise import (
    Item,
    EmployeeTypes,
    MachineType,
    Machine,
    Inventory,
    ItemPrice,
    ItemOrder,
    ProductionDepartment,
    ProductionEmployee,
    PurchasingDepartment,
    PurchasingEmployee,
    SalesDepartment,
    SalesEmployee,
    SupervisorAdminDepartment,
    SupportDepartment,
    SupportEmployee,
)


router = InferringRouter(prefix="/enterprise")


class Message(BaseModel):
    message: str


@router.get("/poll/sales_department", summary="Get the sales department", response_description="The sales departments", responses=make_checked_sim_responses())
def sales_department() -> SalesDepartment:
    return checked_sim().current_state.enterprise.sales_department


@router.get("/poll/purchasing_department", summary="Get the purchasing department", response_description="The purchasing departments", responses=make_checked_sim_responses())
def purchasing_department() -> PurchasingDepartment:
    return checked_sim().current_state.enterprise.purchasing_department


@router.get("/poll/production_department", summary="Get the production department", response_description="The production departments", responses=make_checked_sim_responses())
def production_department() -> ProductionDepartment:
    return checked_sim().current_state.enterprise.production_department


@router.get("/poll/support_department", summary="Get the support department", response_description="The support departments", responses=make_checked_sim_responses())
def support_department() -> SupportDepartment:
    return checked_sim().current_state.enterprise.support_department


@router.get("/poll/supervisor_admin_department", summary="Get the supervisor admin department", response_description="The supervisor admin departments", responses=make_checked_sim_responses())
def supervisor_admin_department() -> SupervisorAdminDepartment:
    return checked_sim().current_state.enterprise.supervisor_admin_department


@router.get("/poll/employee", summary="List all the employees", response_description="A list of all the employees", responses=make_checked_sim_responses())
def employees() -> List[EmployeeTypes]:
    return checked_sim().current_state.enterprise.employees


@router.get(
    "/poll/job_market", summary="List all the employees available for hire on the job market", response_description="A list of all the employees which are available for hire", responses=make_checked_sim_responses()
)
def job_market() -> List[EmployeeTypes]:
    return checked_sim().current_state.enterprise.job_market


@router.get(
    "/poll/item",
    summary="List all the (types of) items that are either taken as input or produced as output by the machines in the production department",
    response_description="A list of all the (types of) items",
    responses=make_checked_sim_responses(),
)
def items() -> List[Item]:
    return checked_sim().current_state.enterprise.items


@router.get(
    "/poll/machine_type",
    summary="List all the types of machines that are available to be used in the production department",
    response_description="A list of all the types of machines",
    responses=make_checked_sim_responses(),
)
def machine_types() -> List[MachineType]:
    return checked_sim().current_state.enterprise.machine_types


@router.get(
    "/poll/machine", summary="List all the machines that are are present (and potentially usable) in the production department", response_description="A list of all the machines", responses=make_checked_sim_responses()
)
def machines() -> List[Machine]:
    return checked_sim().current_state.enterprise.machines


@router.get(
    "/poll/inventory",
    summary="List the inventory of enterprise: the items it has in stock as well as it's current available funds",
    response_description="The inventory of the enterprise",
    responses=make_checked_sim_responses(),
)
def inventory() -> Inventory:
    return checked_sim().current_state.enterprise.inventory


@router.get(
    "/poll/market_price",
    summary="List all items available on the market to be bought or sold and machine types available to be bought only, with their prices",
    response_description="A list of all the items and machine types on the market",
    responses=make_checked_sim_responses(),
)
def market_prices() -> List[ItemPrice]:
    return checked_sim().current_state.enterprise.market_prices


@router.get(
    "/poll/auto_sell_item",
    summary="List all the items that will be sold automatically in the next step, if any quantity is available, at market prices",
    response_description="A list of all the auto sold items",
    responses=make_checked_sim_responses(),
)
def auto_sell_items() -> List[Item]:
    return checked_sim().current_state.enterprise.auto_sell_items


@router.get(
    "/poll/item_order",
    summary="List all the items or machine types that will be ordered, at specified quantities, in the next step at market prices. For machine types the quantity will be rounded down (floor) to an integer.",
    response_description="A list of all the items or machines to be bought",
    responses=make_checked_sim_responses(),
)
def item_orders() -> List[ItemOrder]:
    return checked_sim().current_state.enterprise.item_orders




@router.get(
    "/poll/analytical_accounting_sim4",
    summary="Get the break-even price for each final sold item (ProcMat1 and ProcMat2)",
    response_description="A dictionary with one break-even price per sold item name",
    responses=make_checked_sim_responses("'Simulation not already created' OR 'Simulation created is not sim4'"),
)
def analytical_accounting_sim4() -> Dict[str, float]:
    sim = checked_sim()
    print(f"sim_name: '{get_sim_name()}'")
    if get_sim_name() != "sim4":
        raise HTTPException(status_code=404, detail="Simulation created is not sim4")
    return sim.analytical_accounting_sim4()


@router.post(
    "/poll/set_market_sell_price_sim4",
    summary="Set new prices for both sold items (ProcMat1 and ProcMat2) in sim4.",
    response_description="Nothing",
    responses=make_checked_sim_and_validation_error_responses(
        http_404_error_description="'Simulation not already created' OR 'Simulation created is not sim4'", http_422_error_description="Validation Error, prices have to be positive values."
    ),
)
def set_market_sell_price_sim4(ProcMat1_unit_price: float, ProcMat2_unit_price: float) -> None:
    sim = checked_sim()
    if get_sim_name() != "sim4":
        raise HTTPException(status_code=404, detail="Simulation created is not sim4")
    if ProcMat1_unit_price <= 0.0 or ProcMat2_unit_price <= 0.0:
        raise HTTPException(status_code=422, detail="Validation Error, prices have to be positive values.")

    ent = sim.current_state.enterprise

    procmat1_item_prices = [item_price for item_price in ent.market_prices if item_price.item.name == "ProcMat1"]
    if len(procmat1_item_prices) != 1:
        raise HTTPException(status_code=500, detail="Internal Server Error, item on market not found")
    else:
        procmat1_item_price = procmat1_item_prices[0]
        procmat1_item_price.unit_price = ProcMat1_unit_price

    procmat2_item_prices = [item_price for item_price in ent.market_prices if item_price.item.name == "ProcMat2"]
    if len(procmat2_item_prices) != 1:
        raise HTTPException(status_code=500, detail="Internal Server Error, item on market not found")
    else:
        procmat2_item_price = procmat2_item_prices[0]
        procmat2_item_price.unit_price = ProcMat2_unit_price
    return None


routers = [router]
