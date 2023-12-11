import csv
import json

temp_instructions = {
    'Program' : list(range(-1,0)),
    'Declaration_list' : list(range(0,2)),
    'Declaration' : list(range(2,3)),
    'Declaration_initial' : list(range(3,4)),
    'Declaration_prime' : list(range(4,6)),
    'Var_declaration_prime' : list(range(6,8)),
    'Fun_declaration_prime' : list(range(8,9)),
    'Type_specifier' : list(range(9,11)),
    'Params' : list(range(11,13)),
    'Param_list' : list(range(13,15)),
    'Param' : list(range(15,16)),
    'Param_prime' : list(range(16,18)),
    'Compound_stmt' : list(range(18,19)),
    'Statement_list' : list(range(19,21)),
    'Statement' : list(range(21,26)),
    'Expression_stmt' : list(range(26,29)),
    'Selection_stmt' : list(range(29,30)),
    'Iteration_stmt' : list(range(30,31)),
    'Return_stmt' : list(range(31,32)),
    'Return_stmt_prime' : list(range(32,34)),
    'Expression' : list(range(34,36)),
    'B' : list(range(36,39)),
    'H' : list(range(39,41)),
    'Simple_expression_zegond' : list(range(41,42)),
    'Simple_expression_prime' : list(range(42,43)),
    'C' : list(range(43,45)),
    'Relop' : list(range(45,47)),
    'Additive_expression' : list(range(47,48)),
    'Additive_expression_prime' : list(range(48,49)),
    'Additive_expression_zegond' : list(range(49,50)),
    'D' : list(range(50,52)),
    'Addop' : list(range(52,54)),
    'Term' : list(range(54,55)),
    'Term_prime' : list(range(55,56)),
    'Term_zegond' : list(range(56,57)),
    'G' : list(range(57,59)),
    'Factor' : list(range(59,62)),
    'Var_call_prime' : list(range(62,64)),
    'Var_prime' : list(range(64,66)),
    'Factor_prime' : list(range(66,68)),
    'Factor_zegond' : list(range(68,70)),
    'Args' : list(range(70,72)),
    'Arg_list' : list(range(72,73)),
    'Arg_list_prime' : list(range(73,75))
}

instructions = {}
for key in temp_instructions.keys():
    instructions[key] = [ins+1 for ins in temp_instructions[key]]




nt_firsts = {key: set() for key in instructions.keys()}

with open('first.csv', 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    for row in csv_reader:
        nt_firsts[row[0]] = set([header[i] for i in range(1, len(row)) if row[i] == '+'])


nt_follows = {key: set() for key in instructions.keys()}

with open('follow.csv', 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    for row in csv_reader:
        nt_follows[row[0]] = set([header[i] for i in range(1, len(row)) if row[i] == '+'])


nt_predict = [set() for i in range(0, 76)]

with open('predict.csv', 'r') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    for row in csv_reader:
        nt_predict[int(row[0]) - 1] = set([i-1 for i in range(1, len(row)) if row[i] == '+'])


parse_table = {}


headers = None
with open('follow.csv', 'r') as file:
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


temp_parse_table = {}

for key in parse_table:
    cs = []
    was__ = False
    for c in key:
        if c == '_':
            was__ = True
            continue
        if was__:
            c = c.upper()
        cs.append(c)
        was__ = False

    new_key = ''.join(cs)
    temp_parse_table[new_key] = parse_table[key]


with open('parse_table.json', 'w') as file:
    json.dump(temp_parse_table, file)






