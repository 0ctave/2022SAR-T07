from pydantic import BaseModel
from typing import List, Union, Literal, Optional


class Named(BaseModel):
    name: str


def name_of(n: Named) -> str:
    return n.name


DepartmentTypeName = Literal["SupportDepartment", "SalesDepartment", "PurchasingDepartment", "SupervisorAdminDepartment", "ProductionDepartment"]


class SupportDepartment(Named):
    type_name: DepartmentTypeName = "SupportDepartment"


class SalesDepartment(Named):
    type_name: DepartmentTypeName = "SalesDepartment"

    minimum_employee_count_for_enterprise_operation: float

    class Config:
        fields = {
            'minimum_employee_count_for_enterprise_operation': {
                'title': "How many minimum employees must be working for sales to be able to be performed"
            }
        }

class PurchasingDepartment(Named):
    type_name: DepartmentTypeName = "PurchasingDepartment"
    minimum_employee_count_for_enterprise_operation: float

    class Config:
        fields = {
            'minimum_employee_count_for_enterprise_operation': {
                'title': "How many minimum employees must be working for purchases to be able to be performed"
            }
        }


class SupervisorAdminDepartment(Named):
    type_name: DepartmentTypeName = "SupervisorAdminDepartment"
    supervisors_needed_per_supervised_employee: float

    class Config:
        fields = {
            'supervisors_needed_per_supervised_employee': {
                'title': "The number of employees in the SupervisorAdminDepartment that need to be working in order for the ProductionDepartment to be operational"
            }
        }


class ProductionDepartment(Named):
    type_name: DepartmentTypeName = "ProductionDepartment"


DepartmentTypes = Union[SupportDepartment, SalesDepartment, PurchasingDepartment, SupervisorAdminDepartment, ProductionDepartment]


class Item(Named):
    type_name: Literal["Item"] = "Item"
    unit: str

    class Config:
        fields = {
            'unit': {
                'title': "The unit of measurement for this iteam"
            }
        }


class ItemQuantity(BaseModel):
    type_name: Literal["ItemQuantity"] = "ItemQuantity"
    item: Item
    quantity: float

    class Config:
        fields = {
            'item': {
                'title': "The item of which this quantity measures."
            },
            'quantity': {
                'title': "The amount of the item."
            }
        }



class MachineType(Named):
    type_name: Literal["MachineType"] = "MachineType"
    inputs_per_item_output: List[ItemQuantity]
    output_item: Item
    required_operators_count: float
    nominal_output_rate_items_per_hour: float
    operation_cost_per_hour_in_eur: float
    buy_cost_in_eur: float
    new_delivery_in_hours: int
    error_probability_per_hour_of_operation: float
    error_amount_in_percentage: float

    class Config:
        fields = {
            'item': {
                'title': "The inputs consumed by this machin in order to produce one output item. All need to be available for the machine to operate."
            },
            'output_item': {
                'title': "The Item type of whych the output of the machine will be (exactly one)."
            },
            'required_operators_count': {
                'title': "How many ProductionEmployees are required (exactly) to operate the machine. Without this number is is not operational."
            },
            'nominal_output_rate_items_per_hour': {
                'title': "The max number of items produced per hour (not taking into account input item shortages and machine damage)"
            },
            'operation_cost_per_hour_in_eur': {
                'title': "Cost of operation of the machine (at any output rate) for one hour"
            },
            'buy_cost_in_eur': {
                'title': "The cost of buying the machine"
            },
            'new_delivery_in_hours': {
                'title': "Not used yet. Default 0"
            },
            'error_probability_per_hour_of_operation': {
                'title': "The probability [0.0 - 1.0] that the machine will experience a damage incident after one hour of operation"
            },
            'error_amount_in_percentage': {
                'title': "If the machine does experience damage, the amount of productivity lost as a percentage of nominal output rate"
            }
        }


class Machine(Named):
    type_name: Literal["Machine"] = "Machine"
    machine_type: MachineType
    operating_efficiency_percentage: float
    production_department: ProductionDepartment

    class Config:
        fields = {
            'machine_type': {
                'title': "The type of this machine (to support multiple independent machines with the same MachineType)"
            },
            'operating_efficiency_percentage': {
                'title': "The  current the amount of productivity as a percentage of nominal output rate"
            },
            'production_department': {
                'title': "The production department to which this machine belongs."
            }
        }


EmployeeTypeName = Literal["SupportEmployee", "ProductionEmployee", "SalesEmployee", "PurchasingEmployee", "SupervisorAdminEmployee"]


class SupportEmployee(Named):
    type_name: EmployeeTypeName = "SupportEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    working_hours_per_day: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: SupportDepartment
    repair_percentages_per_hour_per_machine: float
    machine_types_repairable: List[MachineType]
    repairing_machine: Optional[Machine]

    class Config:
        fields = {
            'standard_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) or at home sick."
            },
            'overtime_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) during overtime."
            },
            'max_standard_hours_per_day': {
                'title': "Max hours that can be worked with the standard wage in a day."
            },
            'max_overtime_hours_per_day': {
                'title': "Max hours that can be worked with the overtime wage in a day."
            },
            'working_hours_per_day': {
                'title': "Max total number of hours that can be worked in a day."
            },
            'sickness_probability_per_hour_worked': {
                'title': "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."
            },
            'sickness_duration_in_hours_worked': {
                'title': "The duration in hours of sickness if the employee does become sick."
            },
            'remaining_sickness_in_hours_worked': {
                'title': "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."
            },
            'department': {
                'title': "The department to which this employee belongs."
            },
            'repair_percentages_per_hour_per_machine': {
                'title': "The percentage points of operational capacity that this employee can repair to a machinethey are assigne dto repair."
            },
            'machine_types_repairable': {
                'title': "A list of types of machines which the employee knows how to repair"
            },
            'repairing_machine': {
                'title': "The currently being repaired machine by the employee."
            }
        }


class ProductionEmployee(Named):
    type_name: EmployeeTypeName = "ProductionEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    working_hours_per_day: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: ProductionDepartment
    machine_types_operatable: List[MachineType]
    operating_machine: Optional[Machine]

    class Config:
        fields = {
            'standard_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) or at home sick."
            },
            'overtime_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) during overtime."
            },
            'max_standard_hours_per_day': {
                'title': "Max hours that can be worked with the standard wage in a day."
            },
            'max_overtime_hours_per_day': {
                'title': "Max hours that can be worked with the overtime wage in a day."
            },
            'working_hours_per_day': {
                'title': "Max total number of hours that can be worked in a day."
            },
            'sickness_probability_per_hour_worked': {
                'title': "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."
            },
            'sickness_duration_in_hours_worked': {
                'title': "The duration in hours of sickness if the employee does become sick."
            },
            'remaining_sickness_in_hours_worked': {
                'title': "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."
            },
            'department': {
                'title': "The department to which this employee belongs."
            },
            'machine_types_operatable': {
                'title': "A list of types of machines which the employee knows how to operate"
            },
            'operating_machine': {
                'title': "The currently being operated machine by the employee."
            }
        }


class SalesEmployee(Named):
    type_name: EmployeeTypeName = "SalesEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    working_hours_per_day: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: SalesDepartment

    class Config:
        fields = {
            'standard_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) or at home sick."
            },
            'overtime_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) during overtime."
            },
            'max_standard_hours_per_day': {
                'title': "Max hours that can be worked with the standard wage in a day."
            },
            'max_overtime_hours_per_day': {
                'title': "Max hours that can be worked with the overtime wage in a day."
            },
            'working_hours_per_day': {
                'title': "Max total number of hours that can be worked in a day."
            },
            'sickness_probability_per_hour_worked': {
                'title': "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."
            },
            'sickness_duration_in_hours_worked': {
                'title': "The duration in hours of sickness if the employee does become sick."
            },
            'remaining_sickness_in_hours_worked': {
                'title': "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."
            },
            'department': {
                'title': "The department to which this employee belongs."
            }
        }


class PurchasingEmployee(Named):
    type_name: EmployeeTypeName = "PurchasingEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    working_hours_per_day: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: PurchasingDepartment

    class Config:
        fields = {
            'standard_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) or at home sick."
            },
            'overtime_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) during overtime."
            },
            'max_standard_hours_per_day': {
                'title': "Max hours that can be worked with the standard wage in a day."
            },
            'max_overtime_hours_per_day': {
                'title': "Max hours that can be worked with the overtime wage in a day."
            },
            'working_hours_per_day': {
                'title': "Max total number of hours that can be worked in a day."
            },
            'sickness_probability_per_hour_worked': {
                'title': "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."
            },
            'sickness_duration_in_hours_worked': {
                'title': "The duration in hours of sickness if the employee does become sick."
            },
            'remaining_sickness_in_hours_worked': {
                'title': "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."
            },
            'department': {
                'title': "The department to which this employee belongs."
            }
        }

class SupervisorAdminEmployee(Named):
    type_name: EmployeeTypeName = "SupervisorAdminEmployee"
    standard_hourly_wage: float
    overtime_hourly_wage: float
    max_standard_hours_per_day: float
    max_overtime_hours_per_day: float
    working_hours_per_day: float
    sickness_probability_per_hour_worked: float
    sickness_duration_in_hours_worked: float
    remaining_sickness_in_hours_worked: float
    department: SupervisorAdminDepartment
    department_supervision: ProductionDepartment

    class Config:
        fields = {
            'standard_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) or at home sick."
            },
            'overtime_hourly_wage': {
                'title': "The wage received per hour worked (whether actively assigned to something or not) during overtime."
            },
            'max_standard_hours_per_day': {
                'title': "Max hours that can be worked with the standard wage in a day."
            },
            'max_overtime_hours_per_day': {
                'title': "Max hours that can be worked with the overtime wage in a day."
            },
            'working_hours_per_day': {
                'title': "Max total number of hours that can be worked in a day."
            },
            'sickness_probability_per_hour_worked': {
                'title': "The probability [0.0 - 1.0] that the employee will become sick after one hour of work."
            },
            'sickness_duration_in_hours_worked': {
                'title': "The duration in hours of sickness if the employee does become sick."
            },
            'remaining_sickness_in_hours_worked': {
                'title': "The current remaining hours that the employee will be still sick for. When this drop to 0, the employee is not sick any more."
            },
            'department': {
                'title': "The department to which this employee belongs."
            },
            'department_supervision': {
                'title': "The department which is being supervised by this employee."
            }
        }

EmployeeTypes = Union[SupportEmployee, ProductionEmployee, SalesEmployee, PurchasingEmployee, SupervisorAdminEmployee]


class Inventory(BaseModel):
    type_name: Literal["Inventory"] = "Inventory"
    item_quantities: List[ItemQuantity]
    funds_in_eur: float

    class Config:
        fields = {
            'item_quantities': {
                'title': "A list of The available items in stock (for use in the production department or to be sold) and their quantities"
            },
            'funds_in_eur': {
                'title': "The current the amount of money/funds available to the enterprise"
            }
        }


class ItemPrice(BaseModel):
    type_name: Literal["ItemPrice"] = "ItemPrice"
    item: Item
    unit_price: float

    class Config:
        fields = {
           'item': {
                'title': "The item of which this quantity measures."
            },
            'unit_price': {
                'title': "The price of one unit of this item on the market."
            }
        }


class ItemOrder(BaseModel):
    type_name: Literal["ItemOrder"] = "ItemOrder"
    item: Item
    quantity: float


    class Config:
        fields = {
            'item': {
                'title': "The item of to order."
            },
            'quantity': {
                'title': "The amount of the item to order."
            }
        }


class Enterprise(BaseModel):
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
    auto_sell_items: List[Item]
    item_orders: List[ItemOrder]


class Time(BaseModel):
    type_name: Literal["Time"] = "Time"
    day: int
    hour: int

    class Config:
        fields = {
            'day': {
                'title': "The current day"
            },
            'hour': {
                'title': "The current hour"
            }
        }

class SimulationState(BaseModel):
    type_name: Literal["SimulationState"] = "SimulationState"
    time: Time
    enterprise: Enterprise

    class Config:
        fields = {
            'time': {
                'title': "The time instance at which this state has been achived.finalised."
            },
            'enterprise': {
                'title': "The full status of the enterprise"
            }
        }
