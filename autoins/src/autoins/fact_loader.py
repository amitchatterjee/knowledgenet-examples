import pandas as pd

def load_from_csv(facts, of_type, file_path, converters=None):
    df = pd.read_csv(file_path, converters=converters).to_dict(orient='records')
    for row in df:
        fact = of_type(**row)
        facts.add(fact)
