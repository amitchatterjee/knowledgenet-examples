from autoins.edi_parser import parse_edi
from datetime import datetime
from autoins.entities import ClaimType, Claim, Estimate


def test_parse_edi_single_block():
    payload = "\n".join([
        "STX",
        'CLA,clm1,liability,policy1,2020-02-01T00:00:00,1000,100,VIN1,drv1,OPEN,desc1,ir1',
        'POL,policy1,group1,John Doe,2020-01-01T00:00:00,2021-01-01T00:00:00',
        'DRV,drv1,John Doe,1980-01-01T00:00:00,LIC123,CA',
        'EST,est1,estA,yes,VIN1,clm1,2020-02-02T00:00:00,300.0,repair',
        'EST,est2,estB,False,VIN1,clm1,2020-02-03T00:00:00,150.0,parts',
        'CLH,clm2,collision,policy1,2019-01-01T00:00:00,500,500,VIN2,drv2,CLOSED,desc2,ir2',
        'CLH,clm4,collision,policy1,2019-02-01T00:00:00,600,600,VIN4,drv4,CLOSED,desc4,ir4',
        'LYH,clm3,liability,policy1,2018-01-01T00:00:00,200,200,VIN3,drv3,CLOSED,desc3,ir3',
        'LYH,clm5,liability,policy1,2017-01-01T00:00:00,300,300,VIN5,drv5,CLOSED,desc5,ir5',
        'ETX',
    ])

    reqs = parse_edi(payload)
    assert isinstance(reqs, list)
    assert len(reqs) == 1
    req = reqs[0]
    assert req.claim.id == 'clm1'
    assert req.policy.id == 'policy1'
    assert req.driver.id == 'drv1'
    assert req.estimates and len(req.estimates) == 2
    assert req.collision_history and len(req.collision_history) == 2
    assert req.liability_history and len(req.liability_history) == 2

    # Type validations
    # Claim fields
    assert isinstance(req.claim.filing_date, datetime)
    assert isinstance(req.claim.claimed_amount, float)
    assert isinstance(req.claim.paid_amount, float)
    assert req.claim.type == ClaimType.liability

    # Policy and driver types
    assert isinstance(req.policy.start_date, datetime)
    assert isinstance(req.driver.dob, datetime)

    # Estimates: types for date, amount, certified
    for est in req.estimates:
        assert isinstance(est.date, datetime)
        assert isinstance(est.amount, float)
        assert isinstance(est.certified, bool)

    # History entries are Claim instances with proper types
    for c in (req.collision_history or []) + (req.liability_history or []):
        assert isinstance(c, Claim)
        assert isinstance(c.filing_date, datetime)
        assert isinstance(c.claimed_amount, float)

    # Value validations
    # Claim values
    assert req.claim.claimed_amount == 1000.0
    assert req.claim.paid_amount == 100.0
    assert req.claim.vin == 'VIN1'
    assert req.claim.driver_id == 'drv1'
    assert req.claim.status == 'OPEN'
    assert req.claim.description == 'desc1'
    assert req.claim.incidence_report_id == 'ir1'

    # Policy values
    assert req.policy.id == 'policy1'
    assert req.policy.group_id == 'group1'
    assert req.policy.policy_holder == 'John Doe'
    assert req.policy.start_date == datetime(2020, 1, 1, 0, 0, 0)
    assert req.policy.end_date == datetime(2021, 1, 1, 0, 0, 0)

    # Driver values
    assert req.driver.id == 'drv1'
    assert req.driver.name == 'John Doe'
    assert req.driver.license_number == 'LIC123'
    assert req.driver.license_state == 'CA'

    # Estimates values
    est_map = {e.id: e for e in req.estimates}
    e1 = est_map['est1']
    assert e1.estimator_id == 'estA'
    assert e1.certified is True
    assert e1.vin == 'VIN1'
    assert e1.claim_id == 'clm1'
    assert e1.amount == 300.0
    assert e1.description == 'repair'

    e2 = est_map['est2']
    assert e2.estimator_id == 'estB'
    assert e2.certified is False
    assert e2.amount == 150.0
    assert e2.description == 'parts'

    # History values (sample checks)
    assert req.collision_history[0].id == 'clm2'
    assert req.collision_history[0].claimed_amount == 500.0
    assert req.collision_history[0].status == 'CLOSED'
    assert req.liability_history[0].id == 'clm3'
    assert req.liability_history[0].claimed_amount == 200.0
    assert req.liability_history[0].status == 'CLOSED'

def test_parse_edi_multi_block():
    payload = "\n".join([
        "STX",
        'CLA,clmA,collision,policyA,2021-03-01T00:00:00,1500,150,VINA,drvA,OPEN,descA,irA',
        'ETX',
        'STX',
        'CLA,clmB,liability,policyB,2022-04-01T00:00:00,2500,500,VINB,drvB,OPEN,descB,irB',
        'ETX',
    ])

    reqs = parse_edi(payload)
    assert isinstance(reqs, list)
    assert len(reqs) == 2
    assert reqs[0].claim.id == 'clmA'
    assert reqs[1].claim.id == 'clmB'
