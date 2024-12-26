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
        return f'Policy:{self.id}'
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

class Claim:
    def __init__(self, id, policy_id, date, amount, automobile_id, status, description):
        self.id = id
        self.policy_id = policy_id
        self.date = date
        self.amount = amount
        self.status = status
        self.automobile = automobile_id
        self.description = description

class PoliceReport:
    def __init__(self, id, policy, date, description, responsible_parties):
        self.id = id
        self.policy = policy
        self.date = date
        self.description = description
        self.responsible_parties = responsible_parties
