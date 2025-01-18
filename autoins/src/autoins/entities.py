
class Policy:
    def __init__(self, id, policy_holder, start_date, end_date, drivers, automobiles, deductible, max_coverage):
        self.id = id
        self.policy_holder = policy_holder
        self.start_date = start_date
        self.end_date = end_date
        self.drivers = drivers
        self.automobiles = automobiles
        self.deductible = deductible
        self.max_coverage = max_coverage

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

class Automobile:
    def __init__(self, make, model, year, vin):
        self.make = make
        self.model = model
        self.year = year
        self.vin = vin

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
    def __init__(self, id, policy_id, accident_date, claimed_amount, paid_amount, automobile_id, driver_id, status, description, incidence_report_id):
        self.id = id
        self.policy_id = policy_id
        self.accident_date = accident_date
        self.claimed_amount = claimed_amount
        self.paid_amount = paid_amount
        self.driver_id = driver_id
        self.status = status
        self.automobile = automobile_id
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
    def __init__(self, id, source, policy, date, description, responsible_parties, liability_percent):
        self.id = id
        self.source = source
        self.policy = policy
        self.date = date
        self.description = description
        self.responsible_parties = responsible_parties
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
    def __init__(self, id, claim, date, amount, description):
        self.id = id
        self.claim = claim
        self.date = date
        self.amount = amount
        self.description = description

    def __str__(self) -> str:
        return f'Estimate({self.id}, claim={self.claim})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj):
        if isinstance(obj, Estimate):
            return self.id == obj.id
        return False

    def __hash__(self):
        return hash(self.id)

class Adj:
    '''
    The primary purpose of the Adj class is to reduce combinatorial explosion of facts. It also makes audit rules easier to write.
    '''
    def __init__(self, claim: Claim):
        self.claim = claim
        self.policy = None
        self.driver = None
        self.incidence_report = None
        self.history = None
        self.bypass = set()

    def __str__(self) -> str:
        return f'Adj:({self.claim.id})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj):
        if isinstance(obj, Adj):
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
