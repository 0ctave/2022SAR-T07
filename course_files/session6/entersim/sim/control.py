# noqa: F405
from typing import Dict, List, Optional, Union
import random
from pprint import pprint
from copy import deepcopy
from math import floor

def print(*args, **kw):
    pass


# from entersim.util.type_discriminator import type_discriminator_validator_maker
from entersim.sim.enterprise import (
    # DepartmentTypeName,
    # DepartmentTypes,
    # EmployeeTypeName,
    EmployeeTypes,
    Enterprise,
    # Inventory,
    Item,
    # ItemOrder,
    ItemPrice,
    ItemPurchase,
    ItemQuantity,
    ItemSale,
    List,
    Machine,
    MachineType,
    Optional,
    ProductionDepartment,
    ProductionEmployee,
    PurchasingDepartment,
    PurchasingEmployee,
    SalesDepartment,
    SalesEmployee,
    SimulationState,
    SupervisorAdminDepartment,
    SupervisorAdminEmployee,
    SupportDepartment,
    SupportEmployee,
    Time,
)

# import networkx as nx


class Simulation:
    def __init__(self, seed: int, enterprise: Enterprise):
        self.seed = seed
        self.rng = random.Random(self.seed)
        self.current_state = SimulationState(time=Time(day=1, hour=0), enterprise=enterprise)
        # self.status = "Initialised"

    def run_one_step(self) -> None:
        self.next_state = deepcopy(self.current_state)
        next_day = self.current_state.time.day
        next_hour = self.current_state.time.hour + 1
        current_max_hours_per_day = max([emp.max_standard_hours_per_day + emp.max_overtime_hours_per_day for emp in self.current_state.enterprise.employees])
        if next_hour == current_max_hours_per_day + 1:
            next_hour = 1
            next_day += 1

        self.next_state.time = Time(day=next_day, hour=next_hour)

        self.operate_one_hour()

        self.current_state = self.next_state
        # print(f"produ", self.current_state.enterprise.production_department.production_in_the_last_hour)
        print(f"New balance: {self.current_state.enterprise.inventory.funds_in_eur}")
        print(f"D: {self.current_state.time.day} / H: {self.current_state.time.hour}")
        print("")

    def run_until_negative_funds(self) -> None:
        while self.current_state.enterprise.inventory.funds_in_eur >= 0:
            self.run_one_step()

    def is_employee_healthy(self, emp: EmployeeTypes) -> bool:
        return emp.remaining_sickness_in_hours_worked <= 0.0

    def is_employee_in_standard_working_hours(self, emp: EmployeeTypes) -> bool:
        return self.next_state.time.hour <= emp.max_standard_hours_per_day

    def is_employee_in_overtime_working_hours(self, emp: EmployeeTypes) -> bool:
        return self.next_state.time.hour > emp.max_standard_hours_per_day and self.next_state.time.hour <= emp.max_standard_hours_per_day + emp.max_overtime_hours_per_day

    def is_employee_in_any_working_hours(self, emp: EmployeeTypes) -> bool:
        return self.is_employee_in_standard_working_hours(emp) or self.is_employee_in_overtime_working_hours(emp)

    def unassign_machines_to_employees(self) -> None:
        # Clear previous assignments to machines
        for emp_prod in self.get_production_department_employees():
            emp_prod.operating_machine = None
        for emp_sup in self.get_support_department_employees():
            emp_sup.repairing_machine = None

    def reassign_machines_to_employees(self) -> None:
        # Clear previous assignments to machines
        self.unassign_machines_to_employees()
        # Assign first the production employees to machines which are working
        for emp_prod in self.get_production_department_employees():
            self.assign_machine_to_production_employee(emp_prod)
        # Assign then the support employees to machines which are damaged
        for emp_sup in self.get_support_department_employees():
            self.assign_machine_to_support_employee(emp_sup)

    def assign_machine_to_production_employee(self, emp: ProductionEmployee) -> None:
        # assign employee to machines, non-optimally (FCFS)
        if self.is_employee_healthy(emp) and self.is_employee_in_any_working_hours(emp):
            if emp.operating_machine is None:
                # find machine types of the type operated by this employee, and assign the employee to them
                for m in self.next_state.enterprise.machines:
                    if m.operating_efficiency_percentage > 0.0 and m.machine_type in emp.machine_types_operatable:
                        # find other employees who may be operating this machine
                        other_operator_count = len([emp2 for emp2 in self.get_production_department_employees() if emp2.operating_machine is not None and emp2.operating_machine.name == m.name])
                        if other_operator_count + 1 <= m.machine_type.required_operators_count:
                            emp.operating_machine = m
                            print(f"Assigning employee {emp.name} operating machine: {m.name}")
                            return

    def assign_machine_to_support_employee(self, emp: SupportEmployee) -> None:
        # assign employee to machines, non-optimally (FCFS)
        if self.is_employee_healthy(emp) and self.is_employee_in_any_working_hours(emp):
            if emp.repairing_machine is None:
                # find machine types of the type repaired by this employee, and assign the employee to them
                for m in self.next_state.enterprise.machines:
                    if m.operating_efficiency_percentage < 100.0 and m.machine_type in emp.machine_types_repairable:
                        # find other employee who may be repairing this machine
                        other_repairer_count = len([emp2 for emp2 in self.get_support_department_employees() if emp2.repairing_machine is not None and emp2.repairing_machine.name == m.name])
                        if other_repairer_count == 0:
                            emp.repairing_machine = m
                            print(f"Assigning employee {emp.name} repairing machine: {m.name}")
                            return

    def pay_wages(self) -> None:
        for emp in self.next_state.enterprise.employees:
            if not self.is_employee_healthy(emp):  # Sick employee
                if self.is_employee_in_any_working_hours(emp):
                    print(f"Sickness Wage for {emp.name}: {-emp.standard_hourly_wage}")
                continue
            else:  # Healthy employee
                if self.is_employee_in_any_working_hours(emp):  # in working hours
                    if self.is_employee_in_standard_working_hours(emp):
                        self.next_state.enterprise.inventory.funds_in_eur -= emp.standard_hourly_wage
                        print(f"Standard Wage for {emp.name}: {-emp.standard_hourly_wage}")
                        continue
                    if self.is_employee_in_overtime_working_hours(emp):
                        self.next_state.enterprise.inventory.funds_in_eur -= emp.overtime_hourly_wage
                        print(f"Overtime Wage for {emp.name}: {-emp.overtime_hourly_wage}")
                        continue

    def update_sickness(self) -> None:
        for emp in self.next_state.enterprise.employees:
            # update the remaining hours of sickness for the employee, only standard working hours count
            if not self.is_employee_healthy(emp) and self.is_employee_in_standard_working_hours(emp):
                emp.remaining_sickness_in_hours_worked = max(0.0, emp.remaining_sickness_in_hours_worked - 1)

    def make_employees_sick_randomly(self) -> None:
        for emp in self.next_state.enterprise.employees:
            # make employees sick
            if self.is_employee_healthy(emp):
                if self.rng.random() < emp.sickness_probability_per_hour_worked:
                    emp.remaining_sickness_in_hours_worked = emp.sickness_duration_in_hours_worked
                    print(f"Making employee {emp.name} unhealthy for {emp.remaining_sickness_in_hours_worked}")

    # reset operation logs of machines
    def reset_operation_logs_in_production(self) -> None:
        for m in self.next_state.enterprise.machines:
            m.output_in_last_hour = 0
            m.operation_in_last_hour = False
        self.get_production_department().consumption_in_the_last_hour = []
        self.get_production_department().production_in_the_last_hour = []

    # create errors in machines
    def damage_machines_randomly(self) -> None:
        for m in self.next_state.enterprise.machines:
            if self.rng.random() < m.machine_type.error_probability_per_hour_of_operation:
                m.operating_efficiency_percentage = max(0, m.operating_efficiency_percentage - m.machine_type.error_amount_in_percentage)
                print(f"Damaging machine {m.name} to operating efficiency {m.operating_efficiency_percentage}%")

    def operate_production_line(self) -> None:
        produced_item_quantities: List[ItemQuantity] = []
        for m in self.next_state.enterprise.machines:  # production_line.machine_order:
            optional_output_item_quantity = self.operate_machine(m)
            if optional_output_item_quantity is not None:
                produced_item_quantities.append(optional_output_item_quantity)

        # merge item_quantities
        for produced_item_quantity in produced_item_quantities:
            optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(produced_item_quantity.item)
            if optional_inventory_item_quantity is not None:
                optional_inventory_item_quantity.quantity += produced_item_quantity.quantity
            else:
                self.next_state.enterprise.inventory.item_quantities.append(produced_item_quantity)

    def get_item_quantity_in_inventory_by_item(self, item: Item) -> Optional[ItemQuantity]:
        inventory_item_quantities = [inventory_item_quantity for inventory_item_quantity in self.next_state.enterprise.inventory.item_quantities if inventory_item_quantity.item.name == item.name]
        assert len(inventory_item_quantities) in (0, 1)
        if len(inventory_item_quantities) == 1:
            inventory_item_quantity: ItemQuantity = inventory_item_quantities[0]
            return inventory_item_quantity
        if len(inventory_item_quantities) == 0:
            return None
        else:
            raise Exception(f"For item: {item} more than one ItemQuantities were found in the inventory: {inventory_item_quantities}")

    def get_item_price_in_market_by_item(self, item: Union[Item, MachineType]) -> ItemPrice:
        item_prices = [item_price for item_price in self.next_state.enterprise.market_prices if item_price.item.name == item.name]
        assert len(item_prices) in (0, 1)
        if len(item_prices) == 1:
            item_price: ItemPrice = item_prices[0]
            return item_price
        else:
            raise Exception(f"For item/machine: {item} the ItemPrices found were not exactly 1: {item_prices}")

    def operate_machine(self, m: Machine) -> Optional[ItemQuantity]:
        operator_count = len([emp for emp in self.get_production_department_employees() if emp.operating_machine is not None and emp.operating_machine.name == m.name])
        if m.operating_efficiency_percentage <= 0.0:
            print(f"Machine {m.name} is completely damaged")
            return None
        if operator_count < m.machine_type.required_operators_count:
            print(f"Machine {m.name} doesn't have enough operators {operator_count} instead of {m.machine_type.required_operators_count}")
            return None
        if m.operating_efficiency_percentage > 0.0 and operator_count >= m.machine_type.required_operators_count:
            output_rate = m.machine_type.nominal_output_rate_items_per_hour * m.operating_efficiency_percentage / 100.0
            for input_item_quantity in m.machine_type.inputs_per_item_output:
                optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(input_item_quantity.item)
                if optional_inventory_item_quantity is not None:
                    possible_rate = optional_inventory_item_quantity.quantity / input_item_quantity.quantity
                    output_rate = min(output_rate, possible_rate)
                else:
                    # no inventory found: no output, no operating costs (just wages as usual)
                    return None
            if output_rate <= 0.0:
                # no inventory found: no output, no operating costs (just wages as usual)
                print(f"Machine {m.name} cannot operated due to lack of input items.")
                return None

            # OK, consume inventory, produce output and consume operating costs
            for input_item_quantity in m.machine_type.inputs_per_item_output:
                optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(input_item_quantity.item)
                assert optional_inventory_item_quantity is not None
                consumed_input_item_quantity = output_rate * input_item_quantity.quantity
                self.get_production_department().consumption_in_the_last_hour.append(ItemQuantity(item=input_item_quantity.item, quantity=consumed_input_item_quantity))
                optional_inventory_item_quantity.quantity -= consumed_input_item_quantity

            output_item_quantity = ItemQuantity(item=m.machine_type.output_item, quantity=output_rate)
            print(f"Machine {m.name} operated at output rate {output_rate}")

            self.next_state.enterprise.inventory.funds_in_eur -= m.machine_type.operation_cost_per_hour_in_eur
            print(f"Operating costs for machine {m.name}: {-m.machine_type.operation_cost_per_hour_in_eur}")
            self.get_production_department().production_in_the_last_hour.append(deepcopy(output_item_quantity))
            m.operation_in_last_hour = True
            return output_item_quantity
        else:
            # machine offline / fully damaged, no operating costs (just wages as usual)
            print(f"Machine offline/damaged: {m.name}")

            return None

    def perform_repairs(self) -> None:
        for emp in self.next_state.enterprise.employees:
            if isinstance(emp, SupportEmployee) and emp.remaining_sickness_in_hours_worked <= 0.0 and emp.repairing_machine is not None:
                emp.repairing_machine.operating_efficiency_percentage = min(100.0, emp.repairing_machine.operating_efficiency_percentage + emp.repair_percentages_per_hour_per_machine)
                print(f"Repairing: employee {emp.name} repaired machine: {emp.repairing_machine.name} to operating efficiency {emp.repairing_machine.operating_efficiency_percentage}%")

    def sell_items(self) -> None:
        total_sales_income: float = 0
        sales_made: List[ItemSale] = []
        for auto_sell_item in self.next_state.enterprise.auto_sell_items:
            optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(auto_sell_item)
            if optional_inventory_item_quantity is not None and optional_inventory_item_quantity.quantity > 0.0:
                item_price = self.get_item_price_in_market_by_item(auto_sell_item)
                sales_income = optional_inventory_item_quantity.quantity * item_price.unit_price
                sale_made = ItemSale(item=auto_sell_item, quantity=optional_inventory_item_quantity.quantity, total_price=sales_income)
                sales_made.append(sale_made)
                self.next_state.enterprise.inventory.funds_in_eur += sales_income
                total_sales_income += sales_income
                print(f"Income from sale of {optional_inventory_item_quantity}: {sales_income}")
                optional_inventory_item_quantity.quantity = 0
        self.get_sales_department().total_sales_income_in_the_last_hour = total_sales_income
        self.get_sales_department().sales_made_in_the_last_hour = sales_made

    def purchase_items(self) -> None:
        total_purchases_cost: float = 0
        purchases_made: List[ItemPurchase] = []
        for item_order in self.next_state.enterprise.item_orders:
            item_price = self.get_item_price_in_market_by_item(item_order.item)
            item_total_cost = item_order.quantity * item_price.unit_price
            total_purchases_cost += item_total_cost
            purchase_made = ItemPurchase(item=item_order.item, quantity=item_order.quantity, total_price=total_purchases_cost)
            purchases_made.append(purchase_made)

            if isinstance(item_order.item, Item):
                optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(item_order.item)
                if optional_inventory_item_quantity is not None:
                    optional_inventory_item_quantity.quantity += item_order.quantity
                else:
                    self.next_state.enterprise.inventory.item_quantities.append(ItemQuantity(item=item_order.item, quantity=item_order.quantity))
            else:  # isinstance(item_order.item, MachineType)
                int_quantity: int = floor(item_order.quantity)
                for _ in range(int_quantity):
                    existing_machine_count = len(self.next_state.enterprise.machines)
                    pd = self.get_production_department()
                    new_machine = Machine(name=f"{item_order.item.name}_{existing_machine_count+1:02}", machine_type=item_order.item, operating_efficiency_percentage=100, production_department=pd)
                    self.next_state.enterprise.machines.append(new_machine)

            self.next_state.enterprise.inventory.funds_in_eur -= item_total_cost
            print(f"Cost of purchase of {item_order.item.name} x {item_order.quantity} at {item_price.unit_price}/unit: {item_total_cost}")

        self.get_purchasing_department().total_purchasing_spending_in_the_last_hour = total_purchases_cost
        self.get_purchasing_department().purchases_made_in_the_last_hour = purchases_made
        # Make sure to empty!
        self.next_state.enterprise.item_orders = []

    def get_sales_department(self) -> SalesDepartment:
        return self.next_state.enterprise.sales_department
        # return [d for d in self.next_state.enterprise.departments if isinstance(d, SalesDepartment)][0]

    def get_purchasing_department(self) -> PurchasingDepartment:
        return self.next_state.enterprise.purchasing_department
        # return [d for d in self.next_state.enterprise.departments if isinstance(d, PurchasingDepartment)][0]

    def get_supervisor_admin_department(self) -> SupervisorAdminDepartment:
        return self.next_state.enterprise.supervisor_admin_department
        # return [d for d in self.next_state.enterprise.departments if isinstance(d, SupervisorAdminDepartment)][0]

    def get_production_department(self) -> ProductionDepartment:
        return self.next_state.enterprise.production_department
        # return [d for d in self.next_state.enterprise.departments if isinstance(d, ProductionDepartment)][0]

    def get_support_department(self) -> SupportDepartment:
        return self.next_state.enterprise.support_department
        # return [d for d in self.next_state.enterprise.departments if isinstance(d, SupportDepartment)][0]

    def get_sales_department_employees(self) -> List[SalesEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, SalesEmployee) and emp.department.name == self.get_sales_department().name]

    def get_purchasing_department_employees(self) -> List[PurchasingEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, PurchasingEmployee) and emp.department.name == self.get_purchasing_department().name]

    def get_supervision_admin_department_employees(self) -> List[SupervisorAdminEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, SupervisorAdminEmployee) and emp.department.name == self.get_supervisor_admin_department().name]

    def get_support_department_employees(self) -> List[SupportEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, SupportEmployee) and emp.department.name == self.get_support_department().name]

    def get_production_department_employees(self) -> List[ProductionEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, ProductionEmployee) and emp.department.name == self.get_production_department().name]

    def operate_one_hour(self) -> None:
        self.reassign_machines_to_employees()

        working_sad_employees = [emp for emp in self.get_supervision_admin_department_employees() if self.is_employee_healthy(emp) and self.is_employee_in_any_working_hours(emp)]
        working_pd_employees = [emp for emp in self.get_production_department_employees() if self.is_employee_healthy(emp) and self.is_employee_in_any_working_hours(emp) and emp.operating_machine is not None]
        working_sd_employees = [emp for emp in self.get_support_department_employees() if self.is_employee_healthy(emp) and self.is_employee_in_any_working_hours(emp) and emp.repairing_machine is not None]
        working_pud_employees = [emp for emp in self.get_purchasing_department_employees() if self.is_employee_healthy(emp) and self.is_employee_in_any_working_hours(emp)]
        working_sld_employees = [emp for emp in self.get_sales_department_employees() if self.is_employee_healthy(emp) and self.is_employee_in_any_working_hours(emp)]

        # check if supervisor department can function based on the legal minimum requirements. No production operation is allowed without them
        supervisor_employee_count_required = (len(working_pd_employees) + len(working_sd_employees)) * self.get_supervisor_admin_department().supervisors_needed_per_supervised_employee
        is_production_department_operating = supervisor_employee_count_required < len(working_sad_employees)
        self.get_supervisor_admin_department().operation_in_last_hour = is_production_department_operating
        self.get_production_department().operation_in_last_hour = is_production_department_operating
        self.get_support_department().operation_in_last_hour = is_production_department_operating
        if not is_production_department_operating:
            print(f"Production halted! Supervisors required: {supervisor_employee_count_required}, supervisors available: {len(working_sad_employees)} in the SupervisorAdminDepartment to supervise production.")
            # currently just stop the whole supervised production department. Normally, one can choose which employee will not work.
            # unassign employees to machines, to clean things up and to disallow production or repairs
            self.unassign_machines_to_employees()

        # do purchases / add materials
        if len(working_pud_employees) >= self.get_purchasing_department().minimum_employee_count_for_enterprise_operation:
            self.get_purchasing_department().operation_in_last_hour = True
            self.purchase_items()
        else:
            self.get_purchasing_department().operation_in_last_hour = False
            self.get_purchasing_department().total_purchasing_spending_in_the_last_hour = 0
            self.get_purchasing_department().purchases_made_in_the_last_hour = []

            print(
                f"Purchasing halted! Purchasing employees required: {self.get_purchasing_department().minimum_employee_count_for_enterprise_operation}, available: {len(working_pud_employees)} in the PurchasingDepartment to buy items."
            )

        # operate production
        self.reset_operation_logs_in_production()
        if is_production_department_operating:
            self.operate_production_line()
            self.perform_repairs()

        # do sales / get money
        if len(working_sld_employees) >= self.get_sales_department().minimum_employee_count_for_enterprise_operation:
            self.get_sales_department().operation_in_last_hour = True
            self.sell_items()
        else:
            self.get_sales_department().operation_in_last_hour = False
            self.get_sales_department().total_sales_income_in_the_last_hour = 0
            self.get_sales_department().sales_made_in_the_last_hour = []

            print(
                f"Sales halted! Sales employees required: {self.get_sales_department().minimum_employee_count_for_enterprise_operation}, available: {len(working_sld_employees)} in the SalesDepartment to sell produced items."
            )

        # pay wages
        self.pay_wages()
        print(f"Inventory: F={self.next_state.enterprise.inventory.funds_in_eur}", [(iq.item.name, iq.quantity) for iq in self.next_state.enterprise.inventory.item_quantities])
        # update random state (health, hires/fires, damage machines) for next time
        self.update_sickness()
        self.make_employees_sick_randomly()
        self.damage_machines_randomly()

    def employee_hire(self, employee_name: str) -> EmployeeTypes:
        ent = self.current_state.enterprise
        correct_hirable_employees = [employee for employee in ent.job_market if employee.name == employee_name]
        if len(correct_hirable_employees) != 1:
            raise Exception("Validation Error, employee_name not found on the job market")
        else:
            correct_hirable_employee = correct_hirable_employees[0]
            new_employee = deepcopy(correct_hirable_employee)
            name_prefix = ""
            if isinstance(new_employee, SalesEmployee):
                name_prefix = "SELLER"
            elif isinstance(new_employee, PurchasingEmployee):
                name_prefix = "PURCHASER"
            elif isinstance(new_employee, ProductionEmployee):
                name_prefix = "PRODUCER"
            elif isinstance(new_employee, SupportEmployee):
                name_prefix = "SUPPORTER"
            else:  # if isinstance(new_employee, SupervisorAdminEmployee)
                name_prefix = "SUPERVISOR"
            new_employee_id = len([emp for emp in ent.employees if isinstance(emp, type(new_employee))]) + 1
            new_employee.name = f"{name_prefix}_{new_employee_id}"
            ent.employees.append(new_employee)
            return new_employee

    def employee_fire(self, employee_name: str) -> None:
        ent = self.current_state.enterprise
        correct_firable_employees = [employee for employee in ent.employees if employee.name == employee_name]
        if len(correct_firable_employees) != 1:
            raise Exception("Validation Error, employee_name not found in the enterprise")
        else:
            correct_firable_employee = correct_firable_employees[0]
            ent.inventory.funds_in_eur -= correct_firable_employee.firing_cost
            ent.employees = [employee for employee in ent.employees if employee.name != employee_name]
            return None

    def analytical_accounting_sim4(self) -> Dict[str, float]:
        sim = self
        print("Start ANALYTICAL costs")
        # primary_centers = (sim.get_sales_department(), sim.get_production_department())
        # auxiliary_departments = (sim.get_supervisor_admin_department(), sim.get_support_department())

        supervisor_direct_costs = sum([emp.standard_hourly_wage for emp in sim.get_supervision_admin_department_employees()])
        supervisor_total_costs = supervisor_direct_costs
        # repartition_of_supervisor_costs: 30% support, 70% production
        print(f"Supervisor: direct=total={supervisor_total_costs}")

        support_direct_costs = sum([emp.standard_hourly_wage for emp in sim.get_support_department_employees()])
        support_indirect_costs = supervisor_direct_costs * 0.3
        support_total_costs = support_direct_costs + support_indirect_costs
        # repartition_of_support_costs: 80% production, 20% sales
        print(f"Support: direct={support_direct_costs} + indirect={support_indirect_costs} = {support_total_costs}")

        production_direct_costs = sum(
            [emp.standard_hourly_wage for emp in sim.get_production_department_employees()]
            + [machine.machine_type.operation_cost_per_hour_in_eur if machine.operation_in_last_hour else 0.0 for machine in sim.current_state.enterprise.machines],
            0,
        )
        production_indirect_costs = supervisor_total_costs * 0.7 + support_total_costs * 0.8
        production_total_costs = production_direct_costs + production_indirect_costs
        # production_units_of_work = "total items produced"
        production_work_units = sum([iq.quantity for iq in sim.current_state.enterprise.production_department.production_in_the_last_hour])
        assert production_work_units > 0
        production_work_unit_cost = production_total_costs / production_work_units
        print(f"Production: direct={production_direct_costs} + indirect={production_indirect_costs} = {production_total_costs}, #work units={production_work_units} of items, €/wu={production_work_unit_cost}")
        item_cost_of_PM1 = sum([iq.quantity * sim.get_item_price_in_market_by_item(iq.item).unit_price for iq in sim.current_state.enterprise.production_department.consumption_in_the_last_hour if iq.item.name in ["RawMat1"]])
        work_units_cost_of_production_of_PM1 = production_work_unit_cost * sum([iq.quantity for iq in sim.current_state.enterprise.production_department.production_in_the_last_hour if iq.item.name in ["ProcMat1"]])
        item_production_costs_of_PM1 = item_cost_of_PM1 + work_units_cost_of_production_of_PM1

        item_cost_of_PM2 = sum([iq.quantity * sim.get_item_price_in_market_by_item(iq.item).unit_price for iq in sim.current_state.enterprise.production_department.consumption_in_the_last_hour if iq.item.name in ["RawMat2", "RawMat3"]])
        work_units_cost_of_production_of_PM2 = production_work_unit_cost * sum([iq.quantity for iq in sim.current_state.enterprise.production_department.production_in_the_last_hour if iq.item.name in ["ProcMat2"]])
        item_production_costs_of_PM2 = item_cost_of_PM2 + work_units_cost_of_production_of_PM2

        # else:
        #     print(f"Production: direct={production_direct_costs} + indirect={production_indirect_costs} = {production_total_costs}, #work units={production_work_units} of items")

        sales_direct_costs = sum([emp.standard_hourly_wage for emp in sim.get_sales_department_employees()])
        sales_indirect_costs = support_total_costs * 0.2
        sales_total_costs = sales_direct_costs + sales_indirect_costs
        # sales_units_of_work = "1 per 10E of sales"
        sales_work_units = sim.current_state.enterprise.sales_department.total_sales_income_in_the_last_hour / 10.0  # / 10 E
        assert sales_work_units > 0
        sales_work_unit_cost = sales_total_costs / sales_work_units
        print(f"Sales: direct={sales_direct_costs} + indirect={sales_indirect_costs} = {sales_total_costs}, #work units={sales_work_units} of 10€ sales, €/wu={sales_work_unit_cost}")
        # else:
        #     print(f"Sales: direct={sales_direct_costs} + indirect={sales_indirect_costs} = {sales_total_costs}, #work units={sales_work_units} of 10€ sales")
        sales_of_PM1 = sum([itemsale.total_price for itemsale in sim.current_state.enterprise.sales_department.sales_made_in_the_last_hour if itemsale.item.name == "ProcMat1"])
        work_units_cost_of_sales_of_PM1 = (sales_of_PM1 / 10) * sales_work_unit_cost
        break_even_cost_of_PM1 = item_production_costs_of_PM1 + work_units_cost_of_sales_of_PM1
        volume_sold_PM1 = sum([itemsale.quantity for itemsale in sim.current_state.enterprise.sales_department.sales_made_in_the_last_hour if itemsale.item.name == "ProcMat1"])
        break_even_cost_of_PM1_per_unit = break_even_cost_of_PM1 / volume_sold_PM1
        print(f"PM1: break-even/unit={break_even_cost_of_PM1_per_unit}")

        sales_of_PM2 = sum([itemsale.total_price for itemsale in sim.current_state.enterprise.sales_department.sales_made_in_the_last_hour if itemsale.item.name == "ProcMat2"])
        work_units_cost_of_sales_of_PM2 = (sales_of_PM2 / 10) * sales_work_unit_cost
        break_even_cost_of_PM2 = item_production_costs_of_PM2 + work_units_cost_of_sales_of_PM2
        volume_sold_PM2 = sum([itemsale.quantity for itemsale in sim.current_state.enterprise.sales_department.sales_made_in_the_last_hour if itemsale.item.name == "ProcMat2"])
        break_even_cost_of_PM2_per_unit = break_even_cost_of_PM2 / volume_sold_PM2
        print(f"PM2: break-even/unit={break_even_cost_of_PM2_per_unit}")

        print("End ANALYTICAL costs\n")

        return {"ProcMat1": break_even_cost_of_PM1_per_unit, "ProcMat2": break_even_cost_of_PM2_per_unit}


