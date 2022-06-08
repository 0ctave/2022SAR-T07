from copy import copy, deepcopy
from pprint import pprint
from typing import List, Any
from entersim.sim.enterprise import (
    # DepartmentTypeName,
    # DepartmentTypes,
    # EmployeeTypeName,
    # EmployeeTypes,
    EmployeeTypes,
    Enterprise,
    Inventory,
    Item,
    ItemOrder,
    ItemPrice,
    ItemQuantity,
    Machine,
    MachineType,
    ProductionDepartment,
    ProductionEmployee,
    PurchasingDepartment,
    PurchasingEmployee,
    SalesDepartment,
    SalesEmployee,
    # SimulationState,
    SupervisorAdminDepartment,
    SupervisorAdminEmployee,
    SupportDepartment,
    SupportEmployee,
    # Time,
)
from entersim.sim.control import Simulation
from math import ceil

sd01, sld01, pud01, sad01, pd01 = (
    SupportDepartment(name="SupportDept"),
    SalesDepartment(name="SalesDept", minimum_employee_count_for_enterprise_operation=1),
    PurchasingDepartment(name="PurchasingDept", minimum_employee_count_for_enterprise_operation=1),
    SupervisorAdminDepartment(name="SupervisorDept", supervisors_needed_per_supervised_employee=0.1),
    ProductionDepartment(name="ProductionDept"),
)
departments = [sd01, sld01, pud01, sad01, pd01]

item_RM1 = Item(name="RawMat1", unit="litre")
item_RM2 = Item(name="RawMat2", unit="kg")
item_RM3 = Item(name="RawMat3", unit="kg")
item_PM1 = Item(name="ProcMat1", unit="litre")
item_PM2 = Item(name="ProcMat2", unit="kg")

items = [item_RM1, item_RM2, item_RM3, item_PM1, item_PM2]

mt01 = MachineType(
    name="MT1",
    inputs_per_item_output=[ItemQuantity(item=item_RM1, quantity=1)],
    output_item=item_PM1,
    required_operators_count=1,
    nominal_output_rate_items_per_hour=1,
    operation_cost_per_hour_in_eur=1,
    error_probability_per_hour_of_operation=0.012,
    error_amount_in_percentage=45.0,
)
mt02 = MachineType(
    name="MT2",
    inputs_per_item_output=[ItemQuantity(item=item_RM2, quantity=1), ItemQuantity(item=item_RM3, quantity=1)],
    output_item=item_PM2,
    required_operators_count=1,
    nominal_output_rate_items_per_hour=1,
    operation_cost_per_hour_in_eur=1.2,
    error_probability_per_hour_of_operation=0.015,
    error_amount_in_percentage=37.0,
)

machine_types: List[MachineType] = [mt01, mt02]

m01_01 = Machine(name="MT1_01", machine_type=mt01, operating_efficiency_percentage=100, production_department=pd01)
m02_01 = Machine(name="MT2_01", machine_type=mt02, operating_efficiency_percentage=100, production_department=pd01)

machines = [m01_01, m02_01]

base_wage = 10

job_market: List[EmployeeTypes] = []

employees: List[EmployeeTypes] = []
sl_emp01 = SalesEmployee(
    name="SELLER_01",
    standard_hourly_wage=base_wage * 2,
    overtime_hourly_wage=base_wage * 3,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=0,
    firing_cost=base_wage * 2 * 8 * 30,
    department=sld01,
    sickness_probability_per_hour_worked=0.00,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
)
employees.append(sl_emp01)
jm_sl_emp01 = deepcopy(sl_emp01)
jm_sl_emp01.name = "CANDIDATE_" + jm_sl_emp01.name
job_market.append(jm_sl_emp01)



sa_emp01 = SupervisorAdminEmployee(
    name="SUPERVISOR_01",
    standard_hourly_wage=base_wage * 4,
    overtime_hourly_wage=base_wage * 6,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=0,
    firing_cost=base_wage * 4 * 8 * 30,
    department=sad01,
    sickness_probability_per_hour_worked=0.00,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
    department_supervision=pd01,
)
employees.append(sa_emp01)
jm_sa_emp01 = deepcopy(sa_emp01)
jm_sa_emp01.name = "CANDIDATE_" + jm_sa_emp01.name
job_market.append(jm_sa_emp01)

prod_index = 0
for machine_type in machine_types:
    for _ in range(ceil(machine_type.required_operators_count)):
        prod_index += 1
        p_emp_x = ProductionEmployee(
            name=f"PRODUCER_{prod_index:02}",
            standard_hourly_wage=base_wage,
            overtime_hourly_wage=base_wage * 1.5,
            max_standard_hours_per_day=8,
            max_overtime_hours_per_day=0,
            firing_cost=base_wage * 8 * 30,
            department=pd01,
            sickness_probability_per_hour_worked=0.00,
            sickness_duration_in_hours_worked=16,
            remaining_sickness_in_hours_worked=0,
            machine_types_operatable=machine_types,
            operating_machine=None,
        )
        employees.append(p_emp_x)
jm_prod_mt = deepcopy(employees[-1])
jm_prod_mt.name = "CANDIDATE_" + jm_prod_mt.name
job_market.append(jm_prod_mt)


supp_index = 0
for machine_type in machine_types:
    for _ in range(ceil(machine_type.required_operators_count)):
        supp_index += 1
        su_emp_x = SupportEmployee(
            name=f"SUPPORTER_{supp_index:02}",
            standard_hourly_wage=base_wage * 1.5,
            overtime_hourly_wage=base_wage * 1.5 * 1.5,
            max_standard_hours_per_day=8,
            max_overtime_hours_per_day=0,
            firing_cost=base_wage * 1.5 * 8 * 30,
            department=sd01,
            sickness_probability_per_hour_worked=0.00,
            sickness_duration_in_hours_worked=16,
            remaining_sickness_in_hours_worked=0,
            repair_percentages_per_hour_per_machine=3,
            machine_types_repairable=machine_types,
            repairing_machine=None,
        )
        employees.append(su_emp_x)
jm_supp_mt = deepcopy(employees[-1])
jm_supp_mt.name = "CANDIDATE_" + jm_supp_mt.name
job_market.append(jm_supp_mt)

item_quantities: List[ItemQuantity] = []
for machine_type in machine_types:
    for input in machine_type.inputs_per_item_output:
        initial_item = deepcopy(input)
        initial_item.quantity = input.quantity * 8 * 30  # 30 days
        item_quantities.append(initial_item)


market_prices = [
    ItemPrice(item=item_RM1, unit_price=1),
    ItemPrice(item=item_RM2, unit_price=1),
    ItemPrice(item=item_RM3, unit_price=3),
    ItemPrice(item=item_PM1, unit_price=50),
    ItemPrice(item=item_PM2, unit_price=75),
    ItemPrice(item=mt01, unit_price=0),
    ItemPrice(item=mt02, unit_price=0),
]


initial_wages = sum([emp.standard_hourly_wage for emp in employees]) * 8 * 5  # 5 days
initial_machine_buying_capacity = sum([])
inventory = Inventory(item_quantities=item_quantities, funds_in_eur=initial_wages + initial_machine_buying_capacity)


def new_item_orders(factor: float) -> List[ItemOrder]:
    return [
        ItemOrder(item=item_RM1, quantity=factor * 1),
        ItemOrder(item=item_RM2, quantity=factor * 1),
        ItemOrder(item=item_RM3, quantity=factor * 1),
    ]


new_machine_orders = []

enterprise = Enterprise(
    supervisor_admin_department=sad01,
    purchasing_department=pud01,
    sales_department=sld01,
    production_department=pd01,
    support_department=sd01,
    departments=departments,
    employees=employees,
    items=items,
    machine_types=machine_types,
    machines=machines,
    inventory=inventory,
    market_prices=market_prices,
    job_market=job_market,
    auto_sell_items=[item_PM1, item_PM2],
    item_orders=[],
)



def make_sim(seed: Any = 0) -> Simulation:
    return Simulation(seed=seed, enterprise=enterprise)




if __name__ == "__main__":
    teams = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
    team_damages = {}
    for team in teams:
        sim = make_sim(team)
        sim.run_one_step()
        team_damages[team] = []
        while sim.current_state.enterprise.inventory.funds_in_eur >= 0 and sim.current_state.time.day < 29:
            sim.run_one_step()
            team_damages[team].append({machine.name: machine.operating_efficiency_percentage for machine in sim.current_state.enterprise.machines})
            sim.analytical_accounting_sim4()

    for team in teams:
        d_m1 = [d[m01_01.name] for d in team_damages[team]]
        d_m2 = [d[m02_01.name] for d in team_damages[team]]
        print(f"Team {team}: M1: {min(d_m1)}")
        print(f"Team {team}: M2: {min(d_m2)}")

