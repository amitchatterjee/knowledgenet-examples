
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
    def __init__(self, id, policy_id, accident_date, claimed_amount, paid_amount, automobile_id, driver_id, status, description, police_report):
        self.id = id
        self.policy_id = policy_id
        self.accident_date = accident_date
        self.claimed_amount = claimed_amount
        self.paid_amount = paid_amount
        self.driver_id = driver_id
        self.status = status
        self.automobile = automobile_id
        self.description = description
        self.police_report = police_report

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

class PoliceReport:
    def __init__(self, id, policy, date, description, responsible_parties, liability_percent):
        self.id = id
        self.policy = policy
        self.date = date
        self.description = description
        self.responsible_parties = responsible_parties
        self.liability_percent = liability_percent
    def __str__(self) -> str:
        return f'PoliceReport({self.id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, PoliceReport):
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
        self.police_report = None

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
            'police_report': str(self.police_report) if self.police_report else None
        }

class Action:
    columns = ['id','code','claim','action','explain','rank','pay_percent','pay_amount','inactive']

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
        return {
            'id': self.id,
            'code': self.code,
            'claim': self.claim_id,
            'action': self.action,
            'explain': self.explain,
            'rank': self.rank,
            'pay_percent': self.pay_percent if self.pay_percent else 0.0,
            'pay_amount': self.pay_amount if self.pay_amount else 0.0,
            'inactive': self.inactive
        }
    
    def to_csv(self):
        return f"{self.id},{self.code},{self.claim_id},{self.action},{self.explain},{self.rank},{self.pay_percent},{self.pay_amount},{self.inactive}"
