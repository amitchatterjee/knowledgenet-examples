from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Set, ClassVar, Dict

from pydantic import BaseModel, Field

class Driver(BaseModel):
    """Driver associated with a policy."""
    id: str = Field(..., description="Unique driver identifier")
    name: str = Field(..., description="Driver full name")
    dob: datetime = Field(..., description="Date of birth")
    license_number: str = Field(..., description="Driver license number")
    license_state: str = Field(..., description="Driver license issuing state")

    def __str__(self) -> str:
        return f'Driver({self.id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Driver):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

class Group(BaseModel):
    """Policy group for policies containing coverage limits and deductibles.
    """
    id: str = Field(..., description="Unique group identifier")
    collision_deductible: float = Field(..., description="Annual deductible amount for collision claims")
    collision_coverage: float = Field(..., description="Maximum collision coverage amount for the year")
    liability_coverage: float = Field(..., description="Maximum liability coverage amount for the year")

    def __str__(self) -> str:
        return f'Group({self.id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Group):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

class Automobile(BaseModel):
    """Automobile (vehicle) associated with a policy."""
    vin: str = Field(..., description="Vehicle Identification Number (VIN)")
    make: str = Field(..., description="Vehicle manufacturer")
    model: str = Field(..., description="Vehicle model name")
    year: int = Field(..., description="Model year")

    def __str__(self) -> str:
        return f'Automobile({self.vin})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Automobile):
            return self.vin == obj.vin
        return False

    def __hash__(self) -> int:
        return hash(self.vin)

class Policy(BaseModel):
    """Auto insurance policy containing holder, coverage period, vehicles and drivers.
    """
    id: str = Field(..., description="Unique policy identifier")
    group_id: str = Field(..., description="Identifier for the rate/group this policy belongs to")
    policy_holder: str = Field(..., description="Name of the insured policy holder")
    start_date: datetime = Field(..., description="Coverage start datetime")
    end_date: datetime = Field(..., description="Coverage end datetime")
    drivers: List[str] = Field(default_factory=list, description="List of associated driver ids on the policy")
    automobiles: List[str] = Field(default_factory=list, description="List of associated automobile vins on the policy")

    def __str__(self) -> str:
        return f'Policy({self.id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Policy):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

class ClaimType(str, Enum):
    liability = 'liability'
    collision = 'collision'

class Claim(BaseModel):
    """Claim reported against a policy (a loss or incident)"""
    id: str = Field(..., description="Unique claim identifier")
    type: ClaimType = Field(..., description="Type of claim: liability or collision")
    policy_id: str = Field(..., description="Associated policy identifier")
    filing_date: datetime = Field(..., description="Datetime when claim was filed")
    claimed_amount: float = Field(..., description="Amount claimed by claimant")
    paid_amount: float = Field(..., description="Amount paid so far for this claim")
    vin: str = Field(..., description="VIN of the vehicle involved")
    driver_id: str = Field(..., description="Identifier of the involved driver")
    status: str = Field(..., description="Current claim status")
    description: str = Field(..., description="Free-text description of the claim")
    incidence_report_id: str = Field(..., description="Linked incidence report identifier, if any")

    def __str__(self) -> str:
        return f'Claim({self.id}, policy={self.policy_id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Claim):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


class IncidenceReport(BaseModel):
    """Incidence report for an accident or event linked to a claim."""
    id: str = Field(..., description="Unique incidence report identifier")
    source: str = Field(..., description="Source system or reporter of the incident")
    policy: str = Field(..., description="Associated policy identifier")
    accident_date: datetime = Field(..., description="Datetime when the accident occurred")
    description: str = Field(..., description="Detailed description of the incident")
    license_number: str = Field(..., description="Driver license number involved in the incident")
    license_state: str = Field(..., description="State that issued the driver's license")
    vin: str = Field(..., description="Vehicle Identification Number involved in the incident")
    liability_percent: float = Field(..., description="Percent liability assigned for the incident")

    def __str__(self) -> str:
        return f'IncidenceReport({self.id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, IncidenceReport):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


class Estimate(BaseModel):
    id: str
    estimator_id: str
    certified: bool
    vin: str
    claim_id: str
    date: datetime
    amount: float
    description: str
    """Estimate produced by an estimator/vendor for a claim."""
    id: str = Field(..., description="Unique estimate identifier")
    estimator_id: str = Field(..., description="Identifier of the estimator who produced the estimate")
    certified: bool = Field(..., description="If the vendor is certified")
    vin: str = Field(..., description="VIN of the vehicle the estimate applies to")
    claim_id: str = Field(..., description="Associated claim identifier")
    date: datetime = Field(..., description="Datetime when the estimate was produced")
    amount: float = Field(..., description="Estimated amount for repairs/services")
    description: str = Field(..., description="Free-text description of the estimate contents")

    def __str__(self) -> str:
        return f'Estimate({self.id}, claim={self.claim_id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Estimate):
            return self.vin == obj.vin and self.claim_id == obj.claim_id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

class Request(BaseModel):
    claim: Claim
    policy: Optional[Policy] = None
    group: Optional[Group] = None
    driver: Optional[Driver] = None
    automobile: Optional[Automobile] = None
    incidence_report: Optional[IncidenceReport] = None
    collision_history: Optional[List[Claim]] = None
    liability_history: Optional[List[Claim]] = None
    estimates: Optional[List[Estimate]] = None
    bypass: Set[str] = Field(default_factory=set)

    def __str__(self) -> str:
        return f'Request:({self.claim.id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Request):
            return self.claim.id == obj.claim.id
        return False

    def __hash__(self) -> int:
        return hash(self.claim.id)

    def to_dict(self) -> dict:
        return {
            'claim': str(self.claim),
            'policy': str(self.policy) if self.policy else None,
            'driver': str(self.driver) if self.driver else None,
            'incidence_report': str(self.incidence_report) if self.incidence_report else None,
        }

class Action(BaseModel):
    key: ClassVar[str] = 'id'
    columns: ClassVar[Dict[str, type]] = {key: str, 'code': str, 'claim_id': str, 'action': str, 'explain': str, 'rank': int, 'pay_percent': float, 'pay_amount': float, 'inactive': bool}
    
    id: str
    code: str
    claim_id: str
    action: str
    explain: str
    pay_percent: float
    rank: int = 0
    pay_amount: Optional[float] = None
    inactive: bool = True

    def __str__(self) -> str:
        return f'Action({self.id}, code={self.code}, action={self.action})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, Action):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    def to_dict(self) -> dict:
        return {
            key: (0.0 if typ in (int, float) and getattr(self, key) is None else getattr(self, key))
            for (key, typ) in self.columns.items()
        }

