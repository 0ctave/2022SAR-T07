from __future__ import annotations
from pydantic import BaseModel
from typing import List, Union, Literal, Optional


class Named(BaseModel):
    name: str


def name_of(n: Named) -> str:
    return n.name


# DepartmentTypeName = Literal["SupportDepartment", "SalesDepartment", "PurchasingDepartment", "SupervisorAdminDepartment", "ProductionDepartment"]


class SupportDepartment(Named):
    """
    A support department, responsible for the repair of machines which process items in the production departments
    """

    type_name: Literal["SupportDepartment"] = "SupportDepartment"
    operation_in_last_hour: bool = False

    class Config:
        fields = {
            "operation_in_last_hour": {
                "title": """True if the support department operated in the last hour (see also SupervisorAdminDepartment.supervisors_needed_per_supervised_employee), False if not.""",
                "description": """If the department did operate, then the employees may or may not have been assigned to machines, but they were paid their standard or overtime wages in both cases.
                If the department did not operate, then the employees were definitely not assigned to machines and they were paid their standard but not their overtime wages.""",
            },
        }


class SalesDepartment(Named):
    """
    A sales department, responsible for sale of items
    """

    type_name: Literal["SalesDepartment"] = "SalesDepartment"

    minimum_employee_count_for_enterprise_operation: float
    operation_in_last_hour: bool = False
    sales_made_in_the_last_hour: List[ItemSale] = []
    total_sales_income_in_the_last_hour: float = 0

    class Config:
        fields = {
            "minimum_employee_count_for_enterprise_operation": {"title": "How many minimum employees must be working for sales to be able to be performed"},
            "operation_in_last_hour": {
                "title": """True if the sales department operated in the last hour (see minimum_employee_count_for_enterprise_operation), False if not.""",
                "description": """If the department did operate, then the employees may or may not have made sales, but they were paid their standard or overtime wages in both cases.
                If the department did not operate, then the employees performed no sales and they were paid their standard but not their overtime wages.""",
            },
            "sales_made_in_the_last_hour": {"title": "The items sold in the last hour in the form of a list of ItemSale."},
            "total_sales_income_in_the_last_hour": {"title": "The total amount in euro received from all the sales made in the last hour."},
        }


class PurchasingDepartment(Named):
    """
    A purchasing department, responsible for purchases of items and machines
    """

    type_name: Literal["PurchasingDepartment"] = "PurchasingDepartment"
    minimum_employee_count_for_enterprise_operation: float
    operation_in_last_hour: bool = False
    purchases_made_in_the_last_hour: List[ItemPurchase] = []
    total_purchasing_spending_in_the_last_hour: float = 0

    class Config:
        fields = {
            "minimum_employee_count_for_enterprise_operation": {"title": "How many minimum employees must be working for purchases to be able to be performed"},
            "operation_in_last_hour": {
                "title": """True if the purchasing department operated in the last hour (see minimum_employee_count_for_enterprise_operation), False if not.""",
                "description": """If the department did operate, then the employees may or may not have made purchases, but they were paid their standard or overtime wages in both cases.
            If the department did not operate, then the employees performed no purchases and they were paid their standard but not their overtime wages.""",
            },
            "purchases_made_in_the_last_hour": {"title": "The items purchased in the last hour in the form of a list of ItemPurchase."},
            "total_purchasing_spending_in_the_last_hour": {"title": "The total amount in euro spent in all the purchases made in the last hour."},
        }


class SupervisorAdminDepartment(Named):
    """
    A supervisor / administration department, responsible for the supervision of the production and support departments
    """

    type_name: Literal["SupervisorAdminDepartment"] = "SupervisorAdminDepartment"
    supervisors_needed_per_supervised_employee: float
    operation_in_last_hour: bool = False

    class Config:
        fields = {
            "supervisors_needed_per_supervised_employee": {"title": "The number of employees in the SupervisorAdminDepartment that need to be working in order for the ProductionDepartment to be operational"},
            "operation_in_last_hour": {
                "title": """True if the supervisor / administration department operated in the last hour (see supervisors_needed_per_supervised_employee), False if not.""",
                "description": """If the department did operate, then the employyes were paid their standard or overtime wages.
                Additionally, if this department operated, then the production and the support departments definitely also operated (see ProductionDepartment.operation_in_last_hour, SupportDepartment.operation_in_last_hour).
                If the department did not operate, then the employees were paid their standard but not their overtime wages.
                Additionally, then the production and the support departments definitely also did not operate (see ProductionDepartment.operation_in_last_hour, SupportDepartment.operation_in_last_hour).
                """,
            },
        }


class ProductionDepartment(Named):
    """
    A production department, responsible for the operation of machines which process items
    """

    type_name: Literal["ProductionDepartment"] = "ProductionDepartment"
    operation_in_last_hour: bool = False
    consumption_in_the_last_hour: List[ItemQuantity] = []
    production_in_the_last_hour: List[ItemQuantity] = []

    class Config:
        fields = {
            "operation_in_last_hour": {
                "title": """True if the production department operated in the last hour (see also SupervisorAdminDepartment.supervisors_needed_per_supervised_employee), False if not.""",
                "description": """If the department did operate, then the employees may or may not have been assigned to machines, but they were paid their standard or overtime wages in both cases.
                If the department did not operate, then the employees were definitely not assigned to machines and they were paid their standard but not their overtime wages.""",
            },
            "consumption_in_the_last_hour": {"title": "A list of ItemQuantity of all the consumption in the last hour in the production department"},
            "production_in_the_last_hour": {"title": "A list of ItemQuantity of all the production in the last hour in the production department"},
        }


DepartmentTypes = Union[SupportDepartment, SalesDepartment, PurchasingDepartment, SupervisorAdminDepartment, ProductionDepartment]


class Item(Named):
    """
    An item used or produced by machines and sellable or purchasable on the market
    """

    type_name: Literal["Item"] = "Item"
    unit: str

    class Config:
        fields = {"unit": {"title": "The unit of measurement for this item"}}


class ItemQuantity(BaseModel):
    """
    A quantity of  an item
    """

    type_name: Literal["ItemQuantity"] = "ItemQuantity"
    item: Item
    quantity: float

    class Config:
        fields = {"item": {"title": "The item of which this quantity measures."}, "quantity": {"title": "The amount of the item."}}


class MachineType(Named):
    """
    A type of machine with specific inputs and outputs, operation speed, and reliability as well as a given number of employees required to operate, purchasable only on the market
    """

    type_name: Literal["MachineType"] = "MachineType"
    inputs_per_item_output: List[ItemQuantity]
    output_item: Item
    required_operators_count: float
    nominal_output_rate_items_per_hour: float
    operation_cost_per_hour_in_eur: float
    # buy_cost_in_eur: float
    # new_delivery_in_hours: int
    error_probability_per_hour_of_operation: float
    error_amount_in_percentage: float

    class Config:
        fields = {
            "item": {"title": "The inputs consumed by this machin in order to produce one output item. All need to be available for the machine to operate."},
            "output_item": {"title": "The Item type of which the output of the machine will be (exactly one)."},
            "required_operators_count": {"title": "How many ProductionEmployees are required (exactly) to operate the machine. Without this number is is not operational."},
            "nominal_output_rate_items_per_hour": {"title": "The max number of items produced per hour (not taking into account input item shortages and machine damage)"},
            "operation_cost_per_hour_in_eur": {"title": "Cost of operation of the machine (at any output rate) for one hour"},
            # "buy_cost_in_eur": {"title": "The cost of buying the machine"},
            # "new_delivery_in_hours": {"title": "Not used yet. Default 0"},
            "error_probability_per_hour_of_operation": {"title": "The probability [0.0 - 1.0] that the machine will experience a damage incident after one hour of operation"},
            "error_amount_in_percentage": {"title": "If the machine does experience damage, the amount of productivity lost as a percentage of nominal output rate"},
        }


class Machine(Named):
    """
    A specific machine in the production department, transforming its input items into output items when operated by sufficient corresponding production employees and repairable by corresponding support department employees
    """

    type_name: Literal["Machine"] = "Machine"
    machine_type: MachineType
    operating_efficiency_percentage: float
    production_department: ProductionDepartment
    output_in_last_hour: float = 0
    operation_in_last_hour: bool = False

    class Config:
        fields = {
            "machine_type": {"title": "The type of this machine (to support multiple independent machines with the same MachineType)"},
            "operating_efficiency_percentage": {"title": "The  current the amount of productivity as a percentage of nominal output rate"},
            "production_department": {"title": "The production department to which this machine belongs."},
            "output_in_last_hour": {"title": "The quantity of output_item produced in the last hour."},
            "operation_in_last_hour": {"title": "True if the machine operated in the last hour and thus consumed its operation cost (see machine_type.operation_cost_per_hour_in_eur), False if not."},
        }


# EmployeeTypeName = Literal["SupportEmployee", "ProductionEmployee", "SalesEmployee", "PurchasingEmployee", "SupervisorAdminEmployee"]


class SupportEmployee(Named):
    """
    An employee in the support department, allowed to repair machines of specific machine types
    """

    type_name: Literal["SupportEmployee"] = "SupportEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    # working_hours_per_day: float
    firing_cost: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: SupportDepartment
    repair_percentages_per_hour_per_machine: float
    machine_types_repairable: List[MachineType]
    repairing_machine: Optional[Machine]

    class Config:
        fields = {
            "standard_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) or at home sick."},
            "overtime_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) during overtime."},
            "max_standard_hours_per_day": {"title": "Max hours that can be worked with the standard wage in a day."},
            "max_overtime_hours_per_day": {"title": "Max hours that can be worked with the overtime wage in a day."},
            # "working_hours_per_day": {"title": "Max total number of hours that can be worked in a day."},
            "firing_cost": {"title": "Cost in euro of firing this employee."},
            "sickness_probability_per_hour_worked": {"title": "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."},
            "sickness_duration_in_hours_worked": {"title": "The duration in hours of sickness if the employee does become sick."},
            "remaining_sickness_in_hours_worked": {"title": "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."},
            "department": {"title": "The department to which this employee belongs."},
            "repair_percentages_per_hour_per_machine": {"title": "The percentage points of operational capacity that this employee can repair to a machinethey are assigned to repair."},
            "machine_types_repairable": {"title": "A list of types of machines which the employee knows how to repair"},
            "repairing_machine": {"title": "The currently being repaired machine by the employee."},
        }


class ProductionEmployee(Named):
    """
    An employee in the production department, allowed to operate machines of specific machine types
    """

    type_name: Literal["ProductionEmployee"] = "ProductionEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    # working_hours_per_day: float
    firing_cost: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: ProductionDepartment
    machine_types_operatable: List[MachineType]
    operating_machine: Optional[Machine]

    class Config:
        fields = {
            "standard_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) or at home sick."},
            "overtime_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) during overtime."},
            "max_standard_hours_per_day": {"title": "Max hours that can be worked with the standard wage in a day."},
            "max_overtime_hours_per_day": {"title": "Max hours that can be worked with the overtime wage in a day."},
            # "working_hours_per_day": {"title": "Max total number of hours that can be worked in a day."},
            "firing_cost": {"title": "Cost in euro of firing this employee."},
            "sickness_probability_per_hour_worked": {"title": "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."},
            "sickness_duration_in_hours_worked": {"title": "The duration in hours of sickness if the employee does become sick."},
            "remaining_sickness_in_hours_worked": {"title": "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."},
            "department": {"title": "The department to which this employee belongs."},
            "machine_types_operatable": {"title": "A list of types of machines which the employee knows how to operate"},
            "operating_machine": {"title": "The currently being operated machine by the employee."},
        }


class SalesEmployee(Named):
    """
    An employee in the sales department
    """

    type_name: Literal["SalesEmployee"] = "SalesEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    # working_hours_per_day: float
    firing_cost: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: SalesDepartment

    class Config:
        fields = {
            "standard_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) or at home sick."},
            "overtime_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) during overtime."},
            "max_standard_hours_per_day": {"title": "Max hours that can be worked with the standard wage in a day."},
            "max_overtime_hours_per_day": {"title": "Max hours that can be worked with the overtime wage in a day."},
            # "working_hours_per_day": {"title": "Max total number of hours that can be worked in a day."},
            "firing_cost": {"title": "Cost in euro of firing this employee."},
            "sickness_probability_per_hour_worked": {"title": "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."},
            "sickness_duration_in_hours_worked": {"title": "The duration in hours of sickness if the employee does become sick."},
            "remaining_sickness_in_hours_worked": {"title": "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."},
            "department": {"title": "The department to which this employee belongs."},
        }


class PurchasingEmployee(Named):
    """
    An employee in the purchasing department
    """

    type_name: Literal["PurchasingEmployee"] = "PurchasingEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    # working_hours_per_day: float
    firing_cost: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: PurchasingDepartment

    class Config:
        fields = {
            "standard_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) or at home sick."},
            "overtime_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) during overtime."},
            "max_standard_hours_per_day": {"title": "Max hours that can be worked with the standard wage in a day."},
            "max_overtime_hours_per_day": {"title": "Max hours that can be worked with the overtime wage in a day."},
            # "working_hours_per_day": {"title": "Max total number of hours that can be worked in a day."},
            "firing_cost": {"title": "Cost in euro of firing this employee."},
            "sickness_probability_per_hour_worked": {"title": "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."},
            "sickness_duration_in_hours_worked": {"title": "The duration in hours of sickness if the employee does become sick."},
            "remaining_sickness_in_hours_worked": {"title": "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."},
            "department": {"title": "The department to which this employee belongs."},
        }


class SupervisorAdminEmployee(Named):
    """
    An employee in the supervisor / administration department
    """

    type_name: Literal["SupervisorAdminEmployee"] = "SupervisorAdminEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    # working_hours_per_day: float
    firing_cost: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: SupervisorAdminDepartment
    department_supervision: ProductionDepartment

    class Config:
        fields = {
            "standard_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) or at home sick."},
            "overtime_hourly_wage": {"title": "The wage received per hour worked (whether actively assigned to something or not) during overtime."},
            "max_standard_hours_per_day": {"title": "Max hours that can be worked with the standard wage in a day."},
            "max_overtime_hours_per_day": {"title": "Max hours that can be worked with the overtime wage in a day."},
            # "working_hours_per_day": {"title": "Max total number of hours that can be worked in a day."},
            "firing_cost": {"title": "Cost in euro of firing this employee."},
            "sickness_probability_per_hour_worked": {"title": "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."},
            "sickness_duration_in_hours_worked": {"title": "The duration in hours of sickness if the employee does become sick."},
            "remaining_sickness_in_hours_worked": {"title": "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."},
            "department": {"title": "The department to which this employee belongs."},
            "department_supervision": {"title": "The department which is being supervised by this employee."},
        }


EmployeeTypes = Union[SupportEmployee, ProductionEmployee, SalesEmployee, PurchasingEmployee, SupervisorAdminEmployee]


class Inventory(BaseModel):
    """
    The inventory comprising the available stock of items and the available funds
    """

    type_name: Literal["Inventory"] = "Inventory"
    item_quantities: List[ItemQuantity]
    funds_in_eur: float

    class Config:
        fields = {
            "item_quantities": {"title": "A list of The available items in stock (for use in the production department or to be sold) and their quantities"},
            "funds_in_eur": {"title": "The current the amount of money/funds available to the enterprise"},
        }


class ItemPrice(BaseModel):
    """
    The price of selling or buying an item on the market
    """

    type_name: Literal["ItemPrice"] = "ItemPrice"
    item: Union[Item, MachineType]
    unit_price: float

    class Config:
        fields = {"item": {"title": "The item or machine type of which this quantity measures."}, "unit_price": {"title": "The price of one unit of this item or one machine on the market."}}


class ItemOrder(BaseModel):
    """
    The order of a specific quantity of an item (the price will be taken from the market)
    """

    type_name: Literal["ItemOrder"] = "ItemOrder"
    item: Union[Item, MachineType]
    quantity: float

    class Config:
        fields = {
            "item": {"title": "The item or machine type of which to order."},
            "quantity": {"title": "The amount of the item or number of machines to order. If ordering a machine and the quantity is not an integer, the floor of the number is used."},
        }


class ItemSale(BaseModel):
    """
    The sale of a specific quantity of an item at a total given price
    """

    type_name: Literal["ItemSale"] = "ItemSale"
    item: Item
    quantity: float
    total_price: float

    class Config:
        fields = {
            "item": {"title": "The item of which to sell."},
            "quantity": {"title": "The amount of the item to sell."},
            "total_price": {"title": "The total amount in euro received for the sale of the total quantity of the item."},
        }


class ItemPurchase(BaseModel):
    """
    The purchase of a specific quantity of an item at a total given price
    """

    type_name: Literal["ItemPurchase"] = "ItemPurchase"
    item: Union[Item, MachineType]
    quantity: float
    total_price: float

    class Config:
        fields = {
            "item": {"title": "The item or machine type of which to order."},
            "quantity": {"title": "The amount of the item or number of machines to order."},
            "total_price": {"title": "The total amount paid in euro for the purchase of the total quantity of the item or number of machines."},
        }


class Enterprise(BaseModel):
    """
    The enterprise in its entirety
    """

    type_name: Literal["Enterprise"] = "Enterprise"
    supervisor_admin_department: SupervisorAdminDepartment
    purchasing_department: PurchasingDepartment
    sales_department: SalesDepartment
    production_department: ProductionDepartment
    support_department: SupportDepartment
    employees: List[EmployeeTypes]
    items: List[Item]
    machine_types: List[MachineType]
    machines: List[Machine]
    inventory: Inventory
    market_prices: List[ItemPrice]
    job_market: List[EmployeeTypes]
    auto_sell_items: List[Item]
    item_orders: List[ItemOrder]

    class Config:
        fields = {
            "supervisor_admin_department": {"title": "The supervisor / administration department."},
            "purchasing_department": {"title": "The purchasing department."},
            "sales_department": {"title": "The sales department."},
            "production_department": {"title": "The production department."},
            "support_department": {"title": "The support department."},
            "employees": {"title": "The list of all the employees working at the enterprise (in all departments)."},
            "items": {"title": "The list of existing types of items in the enterprise and the market."},
            "machine_types": {"title": "The list of existing types of machines in the enterprise and the market."},
            "machines": {"title": "The list of machines installed in the enterprise in the production department."},
            "inventory": {"title": "The inventory of the enterprise (items and funds)."},
            "market_prices": {"title": "The market prices for selling and buying items and for buying machines."},
            "job_market": {"title": "The list of employees that are available for hire on the job market."},
            "auto_sell_items": {"title": "The list of item types which to auto-sell at the end of each hour."},
            "item_orders": {"title": "The list of items and machines waiting to be bought."},
        }


class Time(BaseModel):
    type_name: Literal["Time"] = "Time"
    day: int
    hour: int

    class Config:
        fields = {"day": {"title": "The current day"}, "hour": {"title": "The current hour"}}


class SimulationState(BaseModel):
    type_name: Literal["SimulationState"] = "SimulationState"
    time: Time
    enterprise: Enterprise

    class Config:
        fields = {"time": {"title": "The time instance at which this state has been achieved / finalized."}, "enterprise": {"title": "The full status of the enterprise"}}


SalesDepartment.update_forward_refs()
PurchasingDepartment.update_forward_refs()
ProductionDepartment.update_forward_refs()
