from pydantic import BaseModel
from typing import List
from pprint import pprint
from fastapi_utils.inferring_router import InferringRouter
from .control import checked_sim, make_checked_sim_responses
from entersim.sim.enterprise import Item, EmployeeTypes, MachineType, Machine, Inventory, ItemPrice, ItemOrder, ProductionDepartment, PurchasingDepartment, SalesDepartment, SupervisorAdminDepartment, SupportDepartment


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


@router.get("/poll/item", summary="List all the (types of) items that are either taken as input or produced as output by the machines in the production department", response_description="A list of all the (types of) items", responses=make_checked_sim_responses())
def items() -> List[Item]:
    return checked_sim().current_state.enterprise.items


@router.get("/poll/machine_type", summary="List all the types of machines that are available to be used in the production department", response_description="A list of all the types of machines", responses=make_checked_sim_responses())
def machine_types() -> List[MachineType]:
    return checked_sim().current_state.enterprise.machine_types


@router.get("/poll/machine", summary="List all the machines that are are present (and potentially usable) in the production department", response_description="A list of all the machines", responses=make_checked_sim_responses())
def machines() -> List[Machine]:
    return checked_sim().current_state.enterprise.machines


@router.get("/poll/inventory", summary="List the inventory of enterprise: the items it has in stock as well as it's current available funds", response_description="The inventory of the enterprise", responses=make_checked_sim_responses())
def inventory() -> Inventory:
    return checked_sim().current_state.enterprise.inventory


@router.get("/poll/market_price", summary="List all items available on the market to be bought or sold, with their prices", response_description="A list of all the items on the market", responses=make_checked_sim_responses())
def market_prices() -> List[ItemPrice]:
    return checked_sim().current_state.enterprise.market_prices


@router.get("/poll/auto_sell_item", summary="List all the items that will be sold automatically in the next step, if any quantity is available, at market prices", response_description="A list of all the auto sold items", responses=make_checked_sim_responses())
def auto_sell_items() -> List[Item]:
    return checked_sim().current_state.enterprise.auto_sell_items


@router.get("/poll/item_order", summary="List all the items that will be ordered, at specified quantities, in the next step at market prices", response_description="A list of all the items to be bought", responses=make_checked_sim_responses())
def item_orders() -> List[ItemOrder]:
    return checked_sim().current_state.enterprise.item_orders


routers = [router]
