import logging
import pandas as pd

class BlueBook:
    # AI-generated code
    def __init__(self, file_path):
        self.data = {}
        df = pd.read_csv(file_path, comment='#', converters={
                    'value': float
                })
        for _, row in df.iterrows():
            key = (row['make'], row['model'], row['year'])
            self.data[key] = row['value']
    
    # 
    def lookup(self, make, model, year):
        return self.data.get((make, model, year), None)
