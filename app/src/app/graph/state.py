from typing import TypedDict

class MeetingState(TypedDict):
    transcript: str
    summary: str
    action_items: str
    email: str
    decision: str # send, edit, regen, stop