from autoins.edi_parser import parse_edi

def test_parse_edi_single_block():
    payload = "\n".join([
        "STX",
        'CLA,clm1,liability,policy1,2020-02-01T00:00:00,1000,100,VIN1,drv1,OPEN,desc1,ir1',
        'POL,policy1,group1,John Doe,2020-01-01T00:00:00,2021-01-01T00:00:00',
        'DRV,drv1,John Doe,1980-01-01T00:00:00,LIC123,CA',
        'EST,est1,estA,True,VIN1,clm1,2020-02-02T00:00:00,300.0,repair',
        'CLH,clm2,collision,policy1,2019-01-01T00:00:00,500,500,VIN2,drv2,CLOSED,desc2,ir2',
        'LYH,clm3,liability,policy1,2018-01-01T00:00:00,200,200,VIN3,drv3,CLOSED,desc3,ir3',
        'ETX',
    ])

    reqs = parse_edi(payload)
    assert isinstance(reqs, list)
    assert len(reqs) == 1
    req = reqs[0]
    assert req.claim.id == 'clm1'
    assert req.policy.id == 'policy1'
    assert req.driver.id == 'drv1'
    assert req.estimates and len(req.estimates) == 1
    assert req.collision_history and len(req.collision_history) == 1
    assert req.liability_history and len(req.liability_history) == 1


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
