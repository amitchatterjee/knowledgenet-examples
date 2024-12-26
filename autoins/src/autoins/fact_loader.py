import pandas as pd

from autoins.entities import Policy

def load_from_csv(facts, file_path, converters=None):
    df = pd.read_csv(file_path, converters=converters).to_dict(orient='records')
    for row in df:
        policy = Policy(**row)
        facts.add(policy)
