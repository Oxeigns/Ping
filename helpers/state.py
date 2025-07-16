from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class GroupState:
    text_filter: bool = True
    media_filter: bool = True
    banned_users: Set[int] = field(default_factory=set)

group_states: Dict[int, GroupState] = {}


def get_state(chat_id: int) -> GroupState:
    state = group_states.get(chat_id)
    if not state:
        state = GroupState()
        group_states[chat_id] = state
    return state
