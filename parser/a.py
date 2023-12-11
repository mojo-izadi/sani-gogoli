import json, csv
import compiler
from anytree import Node, RenderTree


parse_table = None
with open('parse_table.json', 'r') as file:
    parse_table = json.load(file)

# print(parse_table)

instruction_rights = ['Declaration-list',
'Declaration Declaration-list',
'',
'Declaration-initial Declaration-prime',
'Type-specifier ID',
'Fun-declaration-prime',
'Var-declaration-prime',
';',
'[ NUM ] ;',
'( Params ) Compound-stmt',
'int',
'void',
'int ID Param-prime Param-list',
'void',
', Param Param-list',
'',
'Declaration-initial Param-prime',
'[ ]',
'',
'{ Declaration-list Statement-list }',
'Statement Statement-list',
'',
'Expression-stmt',
'Compound-stmt',
'Selection-stmt',
'Iteration-stmt',
'Return-stmt',
'Expression ;',
'break ;',
';',
'if ( Expression ) Statement else Statement',
'while ( Expression ) Statement',
'return Return-stmt-prime',
';',
'Expression ;',
'Simple-expression-zegond',
'ID B',
'= Expression',
'[ Expression ] H',
'Simple-expression-prime',
'= Expression',
'G D C',
'Additive-expression-zegond C',
'Additive-expression-prime C',
'Relop Additive-expression',
'',
'<',
'==',
'Term D',
'Term-prime D',
'Term-zegond D',
'Addop Term D',
'',
'+',
'-',
'Factor G',
'Factor-prime G',
'Factor-zegond G',
'* Factor G',
'',
'( Expression )',
'ID Var-call-prime',
'NUM',
'( Args )',
'Var-prime',
'[ Expression ]',
'',
'( Args )',
'',
'( Expression )',
'NUM',
'Arg-list',
'',
'Expression Arg-list-prime',
', Expression Arg-list-prime',
'']


headers = None
with open('follow.csv', 'r') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    headers = headers[1:]
    headers = {headers[i]: i for i in range(0, len(headers))}

first_node = Node('Program')
stack = ['┤', first_node]

scanner = compiler.Scanner()

def get_next_token():
    return scanner.get_next_token()

token = get_next_token()
token_type = token[1]
token_value = token[2]

while True:
    popped = stack.pop()

    if popped == '┤' and token_value == '┤':
        break
    if headers.__contains__(popped.name):
        token = get_next_token()
        token_type = token[1]
        token_value = token[2]
        if popped.name != token_value:
            print('invalid char')
        continue
    else:
        instruction_to_use = parse_table[popped.name][headers[token_value]]
        states = instruction_rights[instruction_to_use].split(' ')
        states.reverse()
        for state in states:
            stack.append(Node(state, parent=popped))

for pre, fill, node in RenderTree(first_node):
    print("%s%s" % (pre, node.name))





