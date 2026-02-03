from dataclasses import dataclass, field
from datetime import datetime

@dataclass(eq=False)
class Policy:
    id: str
    group_id: str
    policy_holder: str
    start_date: datetime
    end_date: datetime
    drivers: list
    automobiles: list

    def __str__(self) -> str:
        return f'Policy({self.id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, Policy):
            return self.id == obj.id
        return False
    def __hash__(self):
        return hash(self.id)
    
@dataclass(eq=False)
class Group:
    id: str
    collision_deductible: float
    collision_coverage: float
    liability_coverage: float

    def __str__(self) -> str:
        return f'Group({self.id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, Group):
            return self.id == obj.id
        return False
    def __hash__(self):
        return hash(self.id)

@dataclass(eq=False)
class Automobile:
    vin: str
    make: str
    model: str
    year: str
    def __str__(self) -> str:
        return f'Automobile({self.vin})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, Automobile):
            return self.vin == obj.vin
        return False
    def __hash__(self):
        return hash(self.vin)

@dataclass(eq=False)
class Driver:
    id: str
    name: str
    # Date of birth
    dob: str
    license_number: str
    license_state: str
    def __str__(self) -> str:
        return f'Driver({self.id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, Driver):
            return self.id == obj.id
        return False
    def __hash__(self):
        return hash(self.id)

@dataclass(eq=False)
class Claim:
    id: str
    type: str
    policy_id: str
    filing_date: datetime
    claimed_amount: float
    paid_amount: float
    vin: str
    driver_id: str
    status: str
    description: str
    incidence_report_id: str

    def __str__(self) -> str:  # keep original string representation
        return f'Claim({self.id}, policy={self.policy_id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj):  # preserve original equality semantics (id only)
        if isinstance(obj, Claim):
            return self.id == obj.id
        return False

    def __hash__(self):  # preserve original hash semantics (id only)
        return hash(self.id)

@dataclass(eq=False)
class IncidenceReport:
    id: str
    source: str
    policy: str
    accident_date: datetime
    description: str
    license_number: str
    license_state: str
    vin: str
    liability_percent: float
    def __str__(self) -> str:
        return f'IncidenceReport({self.id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, IncidenceReport):
            return self.id == obj.id
        return False
    def __hash__(self):
        return hash(self.id)
    
@dataclass(eq=False)
class Estimate:
    id: str
    estimator_id: str
    approved_vendor: str
    vin: str
    claim_id: str
    date: datetime
    amount: float
    description: str

    def __str__(self) -> str:
        return f'Estimate({self.id}, claim={self.claim_id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj):
        if isinstance(obj, Estimate):
            return self.vin == obj.vin
        return False

    def __hash__(self):
        return hash(self.id)

@dataclass(eq=False)
class ExecutionContext:
    '''
    The primary purpose of the ExecutionContext class is to reduce combinatorial explosion of facts because everything is in one place. It also makes rules authoring easier.
    '''
    claim: Claim
    policy: Policy | None = None
    group: Group | None = None
    driver: Driver | None = None
    automobile: Automobile | None = None
    incidence_report: IncidenceReport | None = None
    collision_history: object | None = None
    liability_history: object | None = None
    estimates: list | None = None
    bypass: set = field(default_factory=set)

    def __str__(self) -> str:
        return f'ExecutionContext:({self.claim.id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj):
        if isinstance(obj, ExecutionContext):
            return self.claim.id == obj.claim.id
        return False

    def __hash__(self):
        return hash(self.claim.id)

    def to_dict(self):
        return {
            'claim': str(self.claim),
            'policy': str(self.policy) if self.policy else None,
            'driver': str(self.driver) if self.driver else None,
            'incidence_report': str(self.incidence_report) if self.incidence_report else None
        }

class Action:
    key='id'
    columns = {key:str,'code':str,'claim_id':str,'action':str,'explain':str,'rank':int,'pay_percent':float,'pay_amount':float,'inactive':bool}

    def __init__(self, id, code, claim_id, action, explain, pay_percent, rank=0, pay_amount=None, inactive=True):
        self.id = id
        self.code = code
        self.claim_id = claim_id
        self.pay_percent = pay_percent
        self.action = action
        self.explain = explain
        self.pay_amount = pay_amount
        self.inactive = inactive
        self.rank = rank

    def __str__(self) -> str:
        return f'Action({self.id}, code={self.code}, action={self.action})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj):
        if isinstance(obj, Action):
            return self.id == obj.id
        return False

    def __hash__(self):
        return hash(self.id)

    def to_dict(self):
        return {key: 0.0 if typ in [int,float] and getattr(self, key) is None else getattr(self, key) 
            for (key,typ) in self.columns.items()}
