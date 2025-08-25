from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AbilityScore(BaseModel):
    name: str
    score: int

class Skill(BaseModel):
    name: str
    ability: str

class Item(BaseModel):
    name: str
    quantity: int = 1
    props: Dict[str, Any] = Field(default_factory=dict)

class Feat(BaseModel):
    name: str
    props: Dict[str, Any] = Field(default_factory=dict)

class Proficiencies(BaseModel):
    saving_throws: Dict[str, bool] = Field(default_factory=dict)

class Character(BaseModel):
    name: str
    level: int
    module: str
    abilities: Dict[str, AbilityScore] = Field(default_factory=dict)
    skills: List[Skill] = Field(default_factory=list)
    items: List[Item] = Field(default_factory=list)
    feats: List[Feat] = Field(default_factory=list)
    notes: Optional[str] = None
    proficiencies: Proficiencies = Field(default_factory=Proficiencies)
