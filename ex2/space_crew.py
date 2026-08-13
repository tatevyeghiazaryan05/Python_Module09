from pydantic import BaseModel, Field, ValidationError, model_validator
from datetime import datetime
from enum import Enum
from typing_extensions import Self


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def validate_rules(self) -> Self:
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")
        has_command = any(
            member.rank == Rank.COMMANDER or member.rank == Rank.CAPTAIN
            for member in self.crew
        )
        if not has_command:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
                )
        if self.duration_days > 365:
            experienced = [m for m in self.crew if m.years_experience >= 5]
            if len(experienced) / len(self.crew) < 0.5:
                raise ValueError(
                    r"Long missions (> 365 days) require at least 50% "
                    "experienced crew (5+ years)"
                    )
        if not all(mem.is_active for mem in self.crew):
            raise ValueError("All crew members must be active")
        return self


def main() -> None:
    print("Space Mission Crew Validation")
    print("=========================================")
    valid_crew = [
        CrewMember(
            member_id="M01",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=42,
            specialization="Mission Command",
            years_experience=15,
            is_active=True,
        ),
        CrewMember(
            member_id="M02",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=35,
            specialization="Navigation",
            years_experience=8,
            is_active=True,
        ),
        CrewMember(
            member_id="M03",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=29,
            specialization="Engineering",
            years_experience=5,
            is_active=True,
        ),
    ]
    valid = SpaceMission(
        mission_name="Mars Colony Establishment",
        mission_id="M2024_MARS",
        destination="Mars",
        launch_date=datetime.now(),
        crew=valid_crew,
        duration_days=900,
        budget_millions=2500.0,
    )
    print("Valid mission created:")
    print(f"Mission: {valid.mission_name}")
    print(f"ID: {valid.mission_id}")
    print(f"Destination: {valid.destination}")
    print(f"Duration: {valid.duration_days} days")
    print(f"Budget: ${valid.budget_millions}M")
    print(f"Crew size: {len(valid.crew)}")
    print("Crew members:")
    for mem in valid.crew:
        print(f"- {mem.name} ({mem.rank.value}) - {mem.specialization}")
    print()
    print("=========================================")
    invalid_crew = [
        CrewMember(member_id="M04",
                   name="John Smith",
                   rank=Rank.LIEUTENANT,
                   age=35,
                   specialization="Navigation",
                   years_experience=8),
        CrewMember(member_id="M05",
                   name="Alice Johnson",
                   rank=Rank.OFFICER,
                   age=29,
                   specialization="Engineering",
                   years_experience=5),
    ]
    try:
        SpaceMission(
            mission_name="Lunar Orbital Research",
            mission_id="M2024_LUNA",
            destination="Moon",
            launch_date=datetime.now(),
            duration_days=180,
            budget_millions=500.0,
            crew=invalid_crew
        )
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            msg = error['msg'].removeprefix("Value error, ")
            print(msg)


if __name__ == "__main__":
    main()
