from typing import (
    Any,
    Callable,
    Container,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypedDict,
    Union,
    cast,
    get_args,
    get_origin,
)

from pydantic import BaseConfig, BaseModel, Field, create_model
from pydantic.fields import FieldInfo
from sqlalchemy import Column, Enum, inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.types import TypeEngine


class Info(TypedDict, total=False):
    alias: str
    allow_mutation: bool
    const: Any
    default: Any
    default_factory: Callable[[], Any]
    description: str
    example: str
    ge: float
    gt: float
    le: float
    lt: float
    max_items: int
    max_length: int
    min_items: int
    min_length: int
    multiple_of: float
    regex: str
    title: str


def is_optional(python_type: type) -> bool:
    return get_origin(python_type) is Union and type(None) in get_args(python_type)


def unchanged(_: str, python_type: type, field: FieldInfo) -> Tuple[type, FieldInfo]:
    return python_type, field


def nonify(_: str, python_type: type, field: FieldInfo) -> Tuple[type, FieldInfo]:
    field.const = field.default = field.default_factory = None
    if is_optional(python_type):
        return python_type, field
    return Optional[python_type], field  # type: ignore[return-value]


class OrmConfig(BaseConfig):
    orm_mode = True


def _extract_python_type(type_engine: TypeEngine) -> type:  # type: ignore[type-arg]
    try:
        return type_engine.python_type
    except (AttributeError, NotImplementedError):
        return cast(type, type_engine.impl.python_type)  # type: ignore[attr-defined]


def infer_python_type(column: Column) -> type:  # type: ignore[type-arg]
    try:
        python_type = _extract_python_type(column.type)
    except (AttributeError, NotImplementedError) as ex:
        raise RuntimeError(
            f"Could not infer the Python type for {column}."
            " Check if the column type has a `python_type` in it or in `impl`"
        ) from ex

    if python_type is list and hasattr(column.type, "item_type"):
        item_type = _extract_python_type(column.type.item_type)
        if column.nullable:
            return Optional[List[item_type]]  # type: ignore[valid-type, return-value]
        return List[item_type]  # type: ignore[valid-type]

    return python_type if not column.nullable else Optional[python_type]  # type: ignore[return-value]


def _get_default_scalar(column: Column) -> Any:  # type: ignore[type-arg]
    if column.default and column.default.is_scalar:
        return column.default.arg
    if column.nullable is False:
        return ...
    return None


def _set_max_length_from_column(field_kwargs: Info, column: Column) -> None:  # type: ignore[type-arg]
    if not isinstance(column.type, Enum):
        sa_type_length = getattr(column.type, "length", None)
        if sa_type_length is not None:
            field_kwargs["max_length"] = sa_type_length


def make_field(column: Column, required=False) -> FieldInfo:  # type: ignore[type-arg]
    info = Info()
    if column.info:
        for key in Info.__annotations__.keys():  # pylint: disable=no-member
            if key in column.info:
                info[key] = column.info[key]  # type: ignore[misc]

    if "max_length" not in info:
        _set_max_length_from_column(info, column)

    if "description" not in info and column.doc:
        info["description"] = column.doc

    if required:
        return cast(FieldInfo, Field(..., **info))  # type: ignore[misc]

    if "default" in info and "default_factory" in info:
        raise ValueError(
            "Both `default` and `default_factory` were specified in info of column"
            f" `{column.name}`. These two attributes are mutually-exclusive"
        )

    if (
        "default" not in info
        and "default_factory" not in info
        and column.default
        and column.default.is_callable
    ):
        return cast(FieldInfo, Field(**info, default_factory=column.default.arg.__wrapped__))  # type: ignore[misc]

    if "default_factory" in info:
        return cast(FieldInfo, Field(**info))

    # pop `default` because it is not a keyword argument of `Field`
    default = info.pop("default") if "default" in info else _get_default_scalar(column)
    return cast(FieldInfo, Field(default, **info))  # type: ignore[misc]


def _fields_from(
    db_model: type,
    *,
    exclude: Optional[Container[str]] = None,
    optional: Optional[Container[str]] = None,
    required: Optional[Container[str]] = None,
    default_transform: Callable[[str, type, FieldInfo], Tuple[type, FieldInfo]],
) -> Dict[str, Tuple[type, FieldInfo]]:
    _exclude, _optional, _required = exclude or [], optional or [], required or []

    if set(_optional).intersection(set(_required)):
        raise ValueError("`optional` and `required` are mutually exclusive")

    mapper = inspect(db_model)
    candidate_attrs = (attr for attr in mapper.attrs if attr.key not in _exclude)

    fields = {}
    for attr in candidate_attrs:
        if isinstance(attr, ColumnProperty) and attr.columns:
            name = attr.key
            column = attr.columns[0]
            python_type = infer_python_type(column)
            field = make_field(column, required=attr.key in _required)
            if attr.key in _optional:
                fields[name] = nonify(name, python_type, field)
            else:
                fields[name] = default_transform(name, python_type, field)
    return fields


def sqlalchemy_to_pydantic(
    db_model: type,
    *,
    exclude: Optional[Container[str]] = None,
    optional: Optional[Container[str]] = None,
    required: Optional[Container[str]] = None,
    default_transform: Callable[
        [str, type, FieldInfo], Tuple[type, FieldInfo]
    ] = unchanged,
    __config__: Type[BaseConfig] = OrmConfig,
) -> Type[BaseModel]:
    fields = _fields_from(
        db_model,
        exclude=exclude,
        optional=optional,
        required=required,
        default_transform=default_transform,
    )
    return cast(
        Type[BaseModel],
        create_model(db_model.__name__, __config__=__config__, **fields),  # type: ignore[arg-type]
    )
