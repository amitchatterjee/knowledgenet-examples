import csv

class BlueBook:
    # AI-generated code
    def __init__(self, file_path):
        self.data = {}
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader((row for row in csvfile if not row.startswith('#')))
            for row in reader:
                key = (row['make'], row['model'], row['year'])
                self.data[key] = float(row['value'])        
    
    def lookup(self, make, model, year):
        return self.data.get((make, model, year), None)
