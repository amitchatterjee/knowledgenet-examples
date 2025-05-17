import csv
from autoins.util import read_csv_and_convert

class BlueBook:
    def __init__(self, file_path):
        self.data = {}
        records = read_csv_and_convert(file_path, converters = {'value': float})
        for row in records:
            key = (row['make'], row['model'], row['year'])
            self.data[key] = float(row['value'])        
    
    def lookup(self, make, model, year):
        return self.data.get((make, model, year), None)
