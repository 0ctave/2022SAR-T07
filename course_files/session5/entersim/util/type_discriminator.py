from pydantic import BaseModel, validator
from typing import Dict, Union, Type, Any, List
from typing_inspect import is_union_type, get_args, is_literal_type
from pprint import pprint
from typeguard import typechecked


@typechecked
def make_type_disctiminator_dict(field_name: str, type_discriminator_field_name: str, cls: Type[BaseModel]) -> Dict[str, Type[BaseModel]]:
    if field_name not in cls.__fields__:
        raise TypeError(f"The referenced field named '{field_name}' is missing in class '{cls.__name__}'")
    field_type = cls.__fields__[field_name].type_
    if not is_union_type(field_type):
        raise TypeError(f"Field {cls.__name__}.{field_name} is not a Union[] type")
    union_classes = get_args(field_type, evaluate=True)
    discriminator_values_class_dict = {}
    for union_class in union_classes:
        if type_discriminator_field_name not in union_class.__fields__:
            raise TypeError(f"The appropriate type discriminator field named '{type_discriminator_field_name}' is missing in class '{union_class.__name__}'")
        union_class_type_discriminator_field_type = union_class.__fields__[type_discriminator_field_name].type_
        if not is_literal_type(union_class_type_discriminator_field_type):
            raise TypeError(f"Field {union_class.__name__}.{union_class_type_discriminator_field_type} is not a Literal[] type")
        type_args = get_args(union_class_type_discriminator_field_type, evaluate=True)
        if len(type_args) != 1:
            raise TypeError(f"Field {union_class.__name__}.{union_class_type_discriminator_field_type} does not exactly one type parameter")
        only_type_arg = type_args[0]
        discriminator_values_class_dict[only_type_arg] = union_class
    return discriminator_values_class_dict


@typechecked
def type_discriminator_validator_maker(field_name: str, type_discriminator_field_name: str = "type_name") -> classmethod:
    @typechecked
    def validate_type_func(cls: Type[BaseModel], value: Union[Dict[str, Any], BaseModel]) -> Any:
        discriminator_values_class_dict = make_type_disctiminator_dict(field_name, type_discriminator_field_name, cls)

        if isinstance(value, BaseModel):
            return value
        else:
            try:
                discriminator_field_value = value[type_discriminator_field_name]
                try:
                    real_class = discriminator_values_class_dict[discriminator_field_value]
                    return real_class(**value)
                except KeyError:
                    raise ValueError(f"Invalid value '{discriminator_field_value}' in discriminator field '{type_discriminator_field_name}' found in: {value}")
            except KeyError:
                raise ValueError(f"No discriminator field '{type_discriminator_field_name}' found in: {value}")

    return validator(field_name, pre=True)(validate_type_func)


@typechecked
def make_list_type_disctiminator_dict(field_name: str, type_discriminator_field_name: str, cls: Type[BaseModel]) -> Dict[str, Type[BaseModel]]:
    if field_name not in cls.__fields__:
        raise TypeError(f"The referenced field named '{field_name}' is missing in class '{cls.__name__}'")
    field_type = cls.__fields__[field_name].type_
    if not is_union_type(field_type):
        raise TypeError(f"Field {cls.__name__}.{field_name} is not a Union[] type")
    union_classes = get_args(field_type, evaluate=True)
    discriminator_values_class_dict = {}
    for union_class in union_classes:
        if type_discriminator_field_name not in union_class.__fields__:
            raise TypeError(f"The appropriate type discriminator field named '{type_discriminator_field_name}' is missing in class '{union_class.__name__}'")
        union_class_type_discriminator_field_type = union_class.__fields__[type_discriminator_field_name].type_
        if not is_literal_type(union_class_type_discriminator_field_type):
            raise TypeError(f"Field {union_class.__name__}.{union_class_type_discriminator_field_type} is not a Literal[] type")
        # type_args = get_args(union_class_type_discriminator_field_type, evaluate=True)
        # if len(type_args) != 1:
        #     raise TypeError(f"Field {union_class.__name__}.{union_class_type_discriminator_field_type} does not exactly one type parameter")
        # only_type_arg = type_args[0]
        discriminator_values_class_dict[union_class.__name__] = union_class
    return discriminator_values_class_dict


@typechecked
def list_type_discriminator_validator_maker(field_name: str, type_discriminator_field_name: str = "type_name") -> classmethod:
    @typechecked
    def validate_type_func(cls: Type[BaseModel], value: List[Union[Dict[str, Any], BaseModel]]) -> Any:
        discriminator_values_class_dict = make_list_type_disctiminator_dict(field_name, type_discriminator_field_name, cls)

        if all([isinstance(element, BaseModel) for element in value]):
            return value
        else:
            result_list: List[BaseModel] = []
            for element in value:
                if isinstance(element, BaseModel):
                    result_list.append(element)
                else:
                    try:
                        discriminator_field_value = getattr(element, type_discriminator_field_name)
                        try:
                            real_class = discriminator_values_class_dict[discriminator_field_value]
                            result_list.append(real_class(**element))
                        except KeyError:
                            raise ValueError(f"Invalid value '{discriminator_field_value}' in discriminator field '{type_discriminator_field_name}' found in: {value}")
                    except KeyError:
                        raise ValueError(f"No discriminator field '{type_discriminator_field_name}' found in: {value}")
            return result_list

    return validator(field_name, pre=True)(validate_type_func)
