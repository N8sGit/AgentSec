from pydantic import BaseModel
from typing import Type

def serialize_message(message: BaseModel) -> dict:
    """Serialize a Pydantic model into a dict."""
    return message.model_dump()

def deserialize_message(data: dict, model: Type[BaseModel]) -> BaseModel:
    """Deserialize a dict into a Pydantic model."""
    return model.model_validate(data)