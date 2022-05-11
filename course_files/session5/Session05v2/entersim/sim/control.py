# noqa: F405
from typing import List, Optional
import random
from pprint import pprint
from copy import deepcopy
# from entersim.util.type_discriminator import type_discriminator_validator_maker
from entersim.sim.enterprise import *
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
                        other_operator_count = len([emp2 for emp2 in self.get_production_department_employees() if emp2.operating_machine == m])
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
                        other_repairer_count = len([emp2 for emp2 in self.get_support_department_employees() if emp2.repairing_machine == m])
                        if other_repairer_count == 0:
                            emp.repairing_machine = m
                            print(f"Assigning employee {emp.name} repairing machine: {m.name}")
                            return

    # TODO: assigne machines to employees before new round, make sure to unassign them if production is off.
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
                emp.remaining_sickness_in_hours_worked = max(0.0, emp.remaining_sickness_in_hours_worked-1)

    def make_employees_sick_randomly(self) -> None:
        for emp in self.next_state.enterprise.employees:
            # make employees sick
            if self.is_employee_healthy(emp):
                if self.rng.random() < emp.sickness_probability_per_hour_worked:
                    emp.remaining_sickness_in_hours_worked = emp.sickness_duration_in_hours_worked
                    print(f"Making employee {emp.name} unhealthy for {emp.remaining_sickness_in_hours_worked}")

    # create errors in machines
    def damage_machines_randomly(self) -> None:
        for m in self.next_state.enterprise.machines:
            if self.rng.random() < m.machine_type.error_probability_per_hour_of_operation:
                m.operating_efficiency_percentage = max(0, m.operating_efficiency_percentage - m.machine_type.error_amount_in_percentage)
                print(f"Damaging machine {m.name} to operating efficiency {m.operating_efficiency_percentage}%")
    
    def operate_production_line(self) -> None:
        # TODO: This should be implemented more generally
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
        inventory_item_quantities = [inventory_item_quantity for inventory_item_quantity in self.next_state.enterprise.inventory.item_quantities if inventory_item_quantity.item == item]
        assert len(inventory_item_quantities) in (0, 1)
        if len(inventory_item_quantities) == 1:
            inventory_item_quantity: ItemQuantity = inventory_item_quantities[0]
            return inventory_item_quantity
        if len(inventory_item_quantities) == 0:
            return None
        else:
            raise Exception(f"For item: {item} more than one ItemQuantities were found in the inventory: {inventory_item_quantities}")

    def get_item_price_in_market_by_item(self, item: Item) -> ItemPrice:
        item_prices = [item_price for item_price in self.next_state.enterprise.market_prices if item_price.item == item]
        assert len(item_prices) in (0, 1)
        if len(item_prices) == 1:
            item_price: ItemPrice = item_prices[0]
            return item_price
        else:
            raise Exception(f"For item: {item} the ItemPrices found were not exactly 1: {item_prices}")

    def operate_machine(self, m: Machine) -> Optional[ItemQuantity]:
        # TODO: This should be implemented more generally
        # pprint(("operate_machine: PE", self.get_production_department_employees()))
        # operators = [emp for emp in self.get_production_department_employees() if emp.operating_machine == m]
        # pprint(("operate_machine: ops", operators))
        operator_count = len([emp for emp in self.get_production_department_employees() if emp.operating_machine == m])
        # pprint(("operate_machine", operator_count))
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
                return None
            
            # OK, consume inventory, produce output and consume operating costs
            for input_item_quantity in m.machine_type.inputs_per_item_output:
                optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(input_item_quantity.item)
                assert optional_inventory_item_quantity is not None
                optional_inventory_item_quantity.quantity -= output_rate*input_item_quantity.quantity
            
            output_item_quantity = ItemQuantity(item=m.machine_type.output_item, quantity=output_rate)
            print(f"Machine {m.name} operated at output rate {output_rate}")
           
            self.next_state.enterprise.inventory.funds_in_eur -= m.machine_type.operation_cost_per_hour_in_eur
            print(f"Operating costs for machine {m.name}: {-m.machine_type.operation_cost_per_hour_in_eur}")
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
        for auto_sell_item in self.next_state.enterprise.auto_sell_items:
            optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(auto_sell_item)
            if optional_inventory_item_quantity is not None:
                item_price = self.get_item_price_in_market_by_item(auto_sell_item)
                sales_income = optional_inventory_item_quantity.quantity * item_price.unit_price
                self.next_state.enterprise.inventory.funds_in_eur += sales_income
                print(f"Income from sale of {optional_inventory_item_quantity}: {sales_income}")
                optional_inventory_item_quantity.quantity = 0

    def purchase_items(self) -> None:
        for item_order in self.next_state.enterprise.item_orders:
            item_price = self.get_item_price_in_market_by_item(item_order.item)
            item_total_cost = item_order.quantity * item_price.unit_price

            optional_inventory_item_quantity = self.get_item_quantity_in_inventory_by_item(item_order.item)
            if optional_inventory_item_quantity is not None:
                optional_inventory_item_quantity.quantity += item_order.quantity
            else:
                self.next_state.enterprise.inventory.item_quantities.append(ItemQuantity(item=item_order.item, quantity=item_order.quantity))

            self.next_state.enterprise.inventory.funds_in_eur -= item_total_cost
            print(f"Cost of purchase of {item_order.item.name} x {item_order.quantity} at {item_price.unit_price}/unit: {item_total_cost}")
        
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
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, SalesEmployee) and emp.department == self.get_sales_department()]

    def get_purchasing_department_employees(self) -> List[PurchasingEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, PurchasingEmployee) and emp.department == self.get_sales_department()]

    def get_supervision_admin_department_employees(self) -> List[SupervisorAdminEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, SupervisorAdminEmployee) and emp.department == self.get_supervisor_admin_department()]

    def get_support_department_employees(self) -> List[SupportEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, SupportEmployee) and emp.department == self.get_support_department()]

    def get_production_department_employees(self) -> List[ProductionEmployee]:
        return [emp for emp in self.next_state.enterprise.employees if isinstance(emp, ProductionEmployee) and emp.department == self.get_production_department()]

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
        if not is_production_department_operating:
            print(f"Production halted! Supervisors required: {supervisor_employee_count_required}, supervisors available: {len(working_sad_employees)} in the SupervisorAdminDepartment to supervise production.")
            # currently just stop the whole supervised production department. Normally, one can choose which employee will not work.
            # unassign employees to machines, to clean things up and to disallow production or repairs
            self.unassign_machines_to_employees()

        # do puchases / add materials
        if len(working_pud_employees) >= self.get_purchasing_department().minimum_employee_count_for_enterprise_operation:
            self.purchase_items()
        else:
            print(f"Purchasing halted! Purchasing employees required: {self.get_purchasing_department().minimum_employee_count_for_enterprise_operation}, available: {len(working_pud_employees)} in the PurchasingDepartment to buy items.")

        # operate production
        if is_production_department_operating:
            self.operate_production_line()
            self.perform_repairs()

        # do sales / get money
        if len(working_sld_employees) >= self.get_sales_department().minimum_employee_count_for_enterprise_operation:
            self.sell_items()
        else:
            print(f"Sales halted! Sales employees required: {self.get_sales_department().minimum_employee_count_for_enterprise_operation}, available: {len(working_sld_employees)} in the SalesDepartment to sell produced items.")

        # pay wages
        self.pay_wages()

        # update random state (health, hires/fires, damage machines) for next time
        self.update_sickness()
        self.make_employees_sick_randomly()
        self.damage_machines_randomly()
