import json, csv
import compiler
from anytree import Node, RenderTree, render


parse_table = None
with open('parse_table.json', 'r') as file:
    parse_table = json.load(file)

# print(parse_table)

instruction_rights = ["DeclarationList", "Declaration DeclarationList", "", "DeclarationInitial DeclarationPrime", "TypeSpecifier ID", "FunDeclarationPrime", "VarDeclarationPrime", ";", "[ NUM ] ;", "( Params ) CompoundStmt", "int", "void", "int ID ParamPrime ParamList", "void", ", Param ParamList", "", "DeclarationInitial ParamPrime", "[ ]", "", "{ DeclarationList StatementList }", "Statement StatementList", "", "ExpressionStmt", "CompoundStmt", "SelectionStmt", "IterationStmt", "ReturnStmt", "Expression ;", "break ;", ";", "if ( Expression ) Statement else Statement", "while ( Expression ) Statement", "return ReturnStmtPrime", ";", "Expression ;", "SimpleExpressionZegond", "ID B", "= Expression", "[ Expression ] H", "SimpleExpressionPrime", "= Expression", "G D C", "AdditiveExpressionZegond C", "AdditiveExpressionPrime C", "Relop AdditiveExpression", "", "<", "==", "Term D", "TermPrime D", "TermZegond D", "Addop Term D", "", "+", "-", "Factor G", "FactorPrime G", "FactorZegond G", "* Factor G", "", "( Expression )", "ID VarCallPrime", "NUM", "( Args )", "VarPrime", "[ Expression ]", "", "( Args )", "", "( Expression )", "NUM", "ArgList", "", "Expression ArgListPrime", ", Expression ArgListPrime", ""]

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
    # print(popped)
    # print(token_value)

    if popped == '┤' and token_value == '┤':
        break
    if headers.__contains__(popped.name):
        if popped.name != token_value and popped.name != 'ID':
            print('invalid char')
        token = get_next_token()
        token_type = token[1]
        token_value = token[2]
        continue
    elif popped.name == '':
        pass
    else:
        temp_token_value = token_value
        if not headers.__contains__(token_value):
            temp_token_value = 'ID'

        
        instruction_to_use = parse_table[popped.name][headers[temp_token_value]]
    
        states = instruction_rights[instruction_to_use].split(' ')
        states.reverse()
        for state in states:
            print(state)
            # for pre, fill, node in RenderTree(first_node):
            #     print("%s%s" % (pre.encode('utf-8'), node.name))
            # print('fuck')                
            stack.append(Node(state, parent=popped))

for pre, fill, node in RenderTree(first_node):
    print("%s%s" % (pre.encode('utf-8'), node.name))
# print(RenderTree(first_node, style=render.ContStyle()))




