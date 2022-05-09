import csv
import json

data = []

new = open("processed.csv", "w")
new.write("prompt,completion,\n")

with open("training-data.csv", "r" ) as f:
    reader = csv.DictReader(f)
    writer = csv.DictWriter(new, ["prompt", "completion"])
    for pair in reader:
        pair["prompt"] = pair['prompt'].strip() + " ->"
        pair['completion'] = " " + pair['completion'].strip() + "\n"
        data.append(pair)
        writer.writerow(pair)

new.close()