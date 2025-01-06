from typing import Dict, Any, List, TypedDict
from tree import StoryChoice

class StoryContent(TypedDict):
    text: str
    description: str

class CombatContent(TypedDict):
    victory_node: str
    defeat_node: str

class NarrativeResult(TypedDict):
    type: str
    content: StoryContent
    choices: List['StoryChoice']

class CombatResult(TypedDict):
    type: str
    combat: Dict[str, Any]

class RecruitmentResult(TypedDict):
    type: str
    content: Dict[str, Any]
