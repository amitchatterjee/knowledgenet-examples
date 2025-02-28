class Policy:
    def __init__(self, id, group_id, policy_holder, start_date, end_date, drivers, automobiles):
        self.id = id
        self.group_id = group_id
        self.policy_holder = policy_holder
        self.start_date = start_date
        self.end_date = end_date
        self.drivers = drivers
        self.automobiles = automobiles

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
    
class Group:
    def __init__(self, id, collision_deductible, collision_coverage, liability_coverage):
        self.id = id
        self.collision_deductible = collision_deductible
        self.collision_coverage = collision_coverage
        self.liability_coverage = liability_coverage

    def __str__(self) -> str:
        return f'Group({self.id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, Policy):
            return self.id == obj.id
        return False
    def __hash__(self):
        return hash(self.id)

class Automobile:
    def __init__(self, vin, make, model, year):
        self.vin = vin
        self.make = make
        self.model = model
        self.year = year
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

class Driver:
    def __init__(self, id, name, dob, license_number, license_state):
        self.id = id
        self.name = name
        self.dob = dob
        self.license_number = license_number
        self.license_state = license_state
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

class Claim:
    def __init__(self, id, type, policy_id, filing_date, claimed_amount, paid_amount, 
                 vin, driver_id, status, description, incidence_report_id):
        self.id = id
        self.type = type
        self.policy_id = policy_id
        self.filing_date = filing_date
        self.claimed_amount = claimed_amount
        self.paid_amount = paid_amount
        self.driver_id = driver_id
        self.status = status
        self.vin = vin
        self.description = description
        self.incidence_report_id = incidence_report_id

    def __str__(self) -> str:
        return f'Claim({self.id}, policy={self.policy_id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, Claim):
            return self.id == obj.id
        return False
    def __hash__(self):
        return hash(self.id)

class IncidenceReport:
    def __init__(self, id, source, policy, accident_date, description, license_number, license_state, vin, liability_percent):
        self.id = id
        self.source = source
        self.policy = policy
        self.accident_date = accident_date
        self.description = description
        self.license_number = license_number
        self.license_state = license_state
        self.vin = vin
        self.liability_percent = liability_percent
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
    
class Estimate:
    def __init__(self, id, estimator_id, approved_vendor, vin, claim_id, date, amount, description):
        self.id = id
        self.estimator_id = estimator_id
        self.approved_vendor = approved_vendor
        self.vin = vin
        self.claim_id = claim_id
        self.date = date
        self.amount = amount
        self.description = description

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

class ExecutionContext:
    '''
    The primary purpose of the ExecutionContext class is to reduce combinatorial explosion of facts because everything is in one place. It also makes rules authoring easier.
    '''
    def __init__(self, claim: Claim):
        self.claim = claim
        self.policy = None
        self.group = None
        self.driver = None
        self.automobile = None
        self.incidence_report = None
        self.collision_history = None
        self.liability_history = None
        self.estimates = None
        self.bypass = set()

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
