from typing import List
from entersim.sim.enterprise import (
    # DepartmentTypeName,
    # DepartmentTypes,
    # EmployeeTypeName,
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


sd01, sld01, pud01, sad01, pd01 = (
    SupportDepartment(name="SD01"),
    SalesDepartment(name="SLD01", minimum_employee_count_for_enterprise_operation=1),
    PurchasingDepartment(name="PUD01", minimum_employee_count_for_enterprise_operation=1),
    SupervisorAdminDepartment(name="SAD01", supervisors_needed_per_supervised_employee=0.1),
    ProductionDepartment(name="PD01"),
)
departments = [sd01, sld01, pud01, sad01, pd01]

item01, item02, item03 = Item(name="I01", unit="kg"), Item(name="I02", unit="kg"), Item(name="I03", unit="kg")
items = [item01, item02, item03]

mt01 = MachineType(
    name="MT01",
    inputs_per_item_output=[ItemQuantity(item=item01, quantity=10)],
    output_item=item02,
    required_operators_count=1,
    nominal_output_rate_items_per_hour=1,
    operation_cost_per_hour_in_eur=5,
    # buy_cost_in_eur=1000,
    # new_delivery_in_hours=0,
    error_probability_per_hour_of_operation=0.0,
    error_amount_in_percentage=0.0,
)
mt02 = MachineType(
    name="MT02",
    inputs_per_item_output=[ItemQuantity(item=item02, quantity=2)],
    output_item=item03,
    required_operators_count=1,
    nominal_output_rate_items_per_hour=1,
    operation_cost_per_hour_in_eur=10,
    # buy_cost_in_eur=2000,
    # new_delivery_in_hours=0,
    error_probability_per_hour_of_operation=0.0,
    error_amount_in_percentage=0.0,
)
machine_types = [mt01, mt02]

m01_01 = Machine(name="M01_01", machine_type=mt01, operating_efficiency_percentage=100, production_department=pd01)
m02_01 = Machine(name="M02_01", machine_type=mt02, operating_efficiency_percentage=100, production_department=pd01)

machines = [m01_01, m02_01]

sl_emp01 = SalesEmployee(
    name="SLE01",
    standard_hourly_wage=10,
    overtime_hourly_wage=15,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=2,
    # working_hours_per_day=8,
    firing_cost=10 * 8 * 30,
    department=sld01,
    sickness_probability_per_hour_worked=0.0,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
)
pu_emp01 = PurchasingEmployee(
    name="PUE01",
    standard_hourly_wage=10,
    overtime_hourly_wage=15,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=2,
    # working_hours_per_day=8,
    firing_cost=10 * 8 * 30,
    department=pud01,
    sickness_probability_per_hour_worked=0.0,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
)
sa_emp01 = SupervisorAdminEmployee(
    name="SAE01",
    standard_hourly_wage=10,
    overtime_hourly_wage=15,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=2,
    # working_hours_per_day=8,
    firing_cost=10 * 8 * 30,
    department=sad01,
    sickness_probability_per_hour_worked=0.0,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
    department_supervision=pd01,
)
p_emp01 = ProductionEmployee(
    name="PE01",
    standard_hourly_wage=10,
    overtime_hourly_wage=15,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=2,
    # working_hours_per_day=8,
    firing_cost=10 * 8 * 30,
    department=pd01,
    sickness_probability_per_hour_worked=0.0,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
    machine_types_operatable=[mt01],
    operating_machine=m01_01,
)
p_emp02 = ProductionEmployee(
    name="PE02",
    standard_hourly_wage=10,
    overtime_hourly_wage=15,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=2,
    # working_hours_per_day=8,
    firing_cost=10 * 8 * 30,
    department=pd01,
    sickness_probability_per_hour_worked=0.0,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
    machine_types_operatable=[mt02],
    operating_machine=m02_01,
)
su_emp01 = SupportEmployee(
    name="SUE02",
    standard_hourly_wage=10,
    overtime_hourly_wage=15,
    max_standard_hours_per_day=8,
    max_overtime_hours_per_day=2,
    # working_hours_per_day=8,
    firing_cost=10 * 8 * 30,
    department=sd01,
    sickness_probability_per_hour_worked=0.0,
    sickness_duration_in_hours_worked=16,
    remaining_sickness_in_hours_worked=0,
    repair_percentages_per_hour_per_machine=5,
    machine_types_repairable=[mt01, mt02],
    repairing_machine=None,
)

employees = [sl_emp01, pu_emp01, sa_emp01, p_emp01, p_emp02, su_emp01]

inventory = Inventory(item_quantities=[ItemQuantity(item=item01, quantity=200)], funds_in_eur=10000)

market_prices = [ItemPrice(item=item01, unit_price=2), ItemPrice(item=item02, unit_price=4), ItemPrice(item=item03, unit_price=40)]

job_market: List[EmployeeTypes] = []

item_orders = [ItemOrder(item=item01, quantity=1), ItemOrder(item=item02, quantity=1)]

enterprise = Enterprise(
    supervisor_admin_department=sad01,
    purchasing_department=pud01,
    sales_department=sld01,
    production_department=pd01,
    support_department=sd01,
    employees=employees,
    items=items,
    machine_types=machine_types,
    machines=machines,
    inventory=inventory,
    market_prices=market_prices,
    job_market=job_market,
    auto_sell_items=[item03],
    item_orders=item_orders,
)


sim = Simulation(seed=0, enterprise=enterprise)
if __name__ == "__main__":
    sim.run_until_negative_funds()
