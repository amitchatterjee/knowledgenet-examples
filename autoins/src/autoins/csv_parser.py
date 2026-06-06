
import csv

def read_csv_and_convert(file_path, converters):
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader((row for row in csvfile if not row.startswith('#')))
        df = []
        for row in reader:
            if converters:
                for key, converter in converters.items():
                    if key in row:
                        row[key] = converter(row[key])
            df.append(row)
    return df