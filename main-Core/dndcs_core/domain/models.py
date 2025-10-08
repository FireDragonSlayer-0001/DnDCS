from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

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


class Companion(BaseModel):
    """Lightweight character-like creature that assists the main character."""

    name: str
    template: Optional[str] = None
    abilities: Dict[str, AbilityScore] = Field(default_factory=dict)
    bonuses: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None

class Character(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    level: int
    module: str
    class_: Optional[str] = Field(default=None, alias="class")
    subclass: Optional[str] = None
    race: Optional[str] = None
    background: Optional[str] = None
    alignment: Optional[str] = None
    hit_points: Optional[int] = None
    hit_dice: Optional[str] = None
    abilities: Dict[str, AbilityScore] = Field(default_factory=dict)
    skills: List[Skill] = Field(default_factory=list)
    items: List[Item] = Field(default_factory=list)
    feats: List[Feat] = Field(default_factory=list)
    notes: Optional[str] = None
    proficiencies: Proficiencies = Field(default_factory=Proficiencies)
    spellcasting: Dict[str, Any] = Field(default_factory=dict)
    companions: List[Companion] = Field(default_factory=list)
