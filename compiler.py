import json, csv
import compiler2
from anytree import Node, RenderTree, render


parse_table = None
with open('grammar_data_files/parse_table.json', 'r') as file:
    parse_table = json.load(file)

# print(parse_table)

with open("grammar_data_files/instruction_rights.json", "r") as f:
    instruction_rights = json.load(f)

headers = None
with open('grammar_data_files/follow.csv', 'r') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    headers = headers[1:]
    headers = {headers[i]: i for i in range(0, len(headers))}
headers[len(headers)] = '/'

first_node = Node('Program')
first_node_ins = Node('-1')

stack = ['┤', first_node]
stack_ins = ['', first_node_ins]

scanner = compiler2.Scanner()

def get_next_token():
    return scanner.get_next_token()

token = get_next_token()
token_type = token[1]
token_value = token[2]

line_number = 1
syntax_errors = []
skip_token = False
invalid_end = False
while True:
    if not skip_token:
        popped = stack.pop()
        popped_ins = stack_ins.pop()
    skip_token = False
    print(popped)
    print(token_value)

    # if token_value == '┤':
    #     print(popped)
    #     print(1)
    if popped == '┤':# or (popped != '┤' and token_value == '┤'):
        if token_value != '┤':
            syntax_errors.append(("EOF" ,"Unexpected" ,line_number))
            invalid_end = True
        break
    if headers.__contains__(popped.name):
        if popped.name != token_value and popped.name != 'ID' and popped.name != 'NUM':
            syntax_errors.append((popped.name ,"missing" ,line_number))
        popped.name = f'({token_type}, {token_value})'
        token = get_next_token()
        token_type = token[1]
        token_value = token[2]
        line_number = token[3]
        continue
    elif popped.name == 'epsilon':
        pass
    else:
        temp_token_value = token_value
        if (not headers.__contains__(token_value)):# and token_type != 'SYMBOL':
            temp_token_value = 'ID'
            if token_type == 'NUM':
                temp_token_value = token_type

        instruction_to_use = parse_table[popped.name][headers[temp_token_value]]
        
        if(instruction_to_use == -1):
            if token_value == '┤':
                syntax_errors.append(("EOF" ,"Unexpected" ,line_number))
                invalid_end = True
                popped.parent = None
                break
            syntax_errors.append( (temp_token_value, "illegal", line_number) )
            token = get_next_token()
            token_type = token[1]
            token_value = token[2]
            line_number = token[3]
            skip_token = True
            # print(temp_token_value)
            # print(popped.name)
            continue
        if(instruction_to_use == "synch"):
            syntax_errors.append( (popped.name, "missing", line_number) )
            # print(temp_token_value)
            # print(popped.name)
            popped.parent = None
            continue
        states = instruction_rights[instruction_to_use].split(' ')
        newStack = []
        newStack_ins = []
        for state in states:
            newStack.append(Node(state if state != '' else 'epsilon', parent=popped))
            newStack_ins.append(Node(state + str(instruction_to_use), parent=popped_ins))

        
        newStack.reverse()
        for n in newStack:
            stack.append(n)

        newStack_ins.reverse()
        for n in newStack_ins:
            stack_ins.append(n)

if invalid_end:
    while len(stack) > 1:
        n = stack.pop()
        n.parent = None

if not invalid_end:
    Node('$', parent=first_node)

f = open("parse_tree.txt", "w", encoding="utf-16")
s = ""
for pre, fill, node in RenderTree(first_node):
    s += "%s%s\n" % (pre, node.name)
    # f.write(s)
f.write(s[:-1])
f.close()

Node('$', parent=first_node_ins)
f = open("syntax_errors.txt", "w", encoding="utf-16")
if not syntax_errors:
    f.write("There is no syntax error.")
else:
    f.writelines([f"#{error[2]} : syntax error, {error[1]} {error[0]}\n" for error in syntax_errors])

f.close()

