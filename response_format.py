from pydantic import BaseModel, ConfigDict
from typing import Literal


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str
    priority: Literal["low", "medium", "high"]
    completed: bool


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "Get a user's profile using their ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"],
                "additionalProperties": False
            }
        }
    }
]