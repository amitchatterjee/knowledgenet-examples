class Policy:
    def __init__(self, id, policy_holder, start_date, end_date, drivers, automobiles, deductible, coverage):
        self.id = id
        self.policy_holder = policy_holder
        self.start_date = start_date
        self.end_date = end_date
        self.drivers = drivers
        self.automobiles = automobiles
        self.deductible = deductible
        self.coverage = coverage

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
    def __init__(self, id, policy_id, date, amount, automobile_id, driver_id, status, description, police_report):
        self.id = id
        self.policy_id = policy_id
        self.date = date
        self.amount = amount
        self.driver_id = driver_id
        self.status = status
        self.automobile = automobile_id
        self.description = description
        self.police_report = police_report

    def __str__(self) -> str:
        return f'Claim({self.id})'
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, obj):
        if isinstance(obj, Claim):
            return self.id == obj.id
        return False
    def __hash__(self):
        return hash(self.id)

class PoliceReport:
    def __init__(self, id, policy, date, description, responsible_parties):
        self.id = id
        self.policy = policy
        self.date = date
        self.description = description
        self.responsible_parties = responsible_parties

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
        return {'Adj': {
            'claim': str(self.claim),
            'policy': str(self.policy) if self.policy else None,
            'driver': str(self.driver) if self.driver else None
            }
        }

class Action:
    def __init__(self, id, claim_id, action, explain, pay_amount):
        self.id = id
        self.claim_id = claim_id
        self.pay_amount = pay_amount
        self.action = action
        self.explain = explain

    def __str__(self) -> str:
        return f'Action({self.id}, action={self.action})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, obj):
        if isinstance(obj, Action):
            return self.id == obj.id
        return False

    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self):
        return {'Action':{
            'id': self.id,
            'claim': self.claim_id,
            'action': self.action,
            'explain': self.explain,
            'pay_amount': self.pay_amount
            }
        }
