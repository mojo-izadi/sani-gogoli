import csv
import json

with open("grammar_data_files/temp_instructions.json", "r") as f:
    temp_instructions = json.load(f)


instructions = {}
for key in temp_instructions.keys():
    instructions[key] = [ins+1 for ins in temp_instructions[key]]


nt_firsts = {key: set() for key in instructions.keys()}

with open('grammar_data_files/first.csv', 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    for row in csv_reader:
        nt_firsts[row[0]] = set([header[i] for i in range(1, len(row)) if row[i] == '+'])


nt_follows = {key: set() for key in instructions.keys()}

with open('grammar_data_files/follow.csv', 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    for row in csv_reader:
        nt_follows[row[0]] = set([header[i] for i in range(1, len(row)) if row[i] == '+'])

with open('grammar_data_files/predict.csv', 'r') as file:
    nt_predict = [set() for i in range(0, len(file.readlines()))]

with open('grammar_data_files/predict.csv', 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    for row in csv_reader:
        nt_predict[int(row[0]) - 1] = set([i-1 for i in range(1, len(row)) if row[i] == '+'])


parse_table = {}


headers = None
with open('grammar_data_files/follow.csv', 'r') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    headers = headers[1:]
    for row in csv_reader:
        nt = row[0]
        parse_table[nt] = [-1 for i in range(0, len(headers))]
        

for nt in instructions.keys():
    nt_parse_data = parse_table[nt]
    for inst in instructions[nt]:
        for t_index in nt_predict[inst]:
            nt_parse_data[t_index] = inst
    nt_parse_data += [-1]


for nt in instructions.keys():
    nt_parse_data = parse_table[nt]
    for i in range(len(headers)):
        if (nt_parse_data[i] == -1) and (nt_follows[nt].__contains__(headers[i])):
            nt_parse_data[i] = "synch"


with open('grammar_data_files/parse_table.json', 'w') as file:
    json.dump(parse_table, file)
