from pydantic import BaseModel, ConfigDict


class ChatHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    message: str
    answer: str

class MessageSchema(BaseModel):
    message_text: str