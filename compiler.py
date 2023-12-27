import json, csv
# import compiler2
from anytree import Node, RenderTree, render
import string
import time







class Data:
    numbers = set([str(i) for i in range(0, 10)])
    letters = set(string.ascii_letters)
    alphanumeric = numbers.union(letters)
    whitespace = set(string.whitespace)
    symbols = {';', ':', ',', '(', ')', '{', '}', '[', ']', '+', '-', '<', '>'}
    equalSymbol = {'='}
    slash = {'/'}
    star = {'*'}
    Eof = {None}
    keywords = {'if', 'else', 'void', 'int', 'while', 'break', 'return'}
    validChars = alphanumeric.union(whitespace)\
            .union(symbols).union(equalSymbol).union(slash).union(star).union(Eof)

class State:
    def next_state(self, currentChar):
        pass


class LastState():
    def get_token_type(self):
        pass

    def is_lookahead(self):
        pass


class ErrorState:
    def is_finish(self):
        pass
    
    def next_state(self, currentChar):
        pass

    def is_lookahead(self):
        pass
    
    def get_error_type(self):
        pass
    

class FirstState(State):
    def next_state(self, currentChar):
        if currentChar in Data.numbers:
            return State1()
        if currentChar in Data.letters:
            return State2()
        if currentChar in Data.symbols:
            return SymbolWithoutLookahead()
        if currentChar in Data.equalSymbol:
            return State3()
        if currentChar in Data.slash:
            return State4()
        if currentChar in Data.whitespace:
            return WhiteSpace()
        if currentChar in Data.star:
            return State8()
        return InvalidInputErrorState()
        

class State1(State):
    def next_state(self, currentChar):
        if currentChar in Data.numbers:
            return self
        if currentChar in Data.letters:
            return InvalidNumberErrorState()
        else:
            return NumberState()
        

class State2(State):
    def next_state(self, currentChar):
        if currentChar in Data.alphanumeric:
            return self
        if currentChar in Data.validChars:
            return Identifier()
        else:
            return InvalidInputErrorState()
        

class State3(State):
    def next_state(self, currentChar):
        if currentChar in Data.equalSymbol:
            return SymbolWithoutLookahead()
        return SymbolWithLookahead()
    

class State4(State):
    def next_state(self, currentChar):
        # if currentChar in Data.slash:
        #     return State5()
        if currentChar in Data.star:
            return State6()
        return SymbolWithLookahead()
    

class State5(State):
    def next_state(self, currentChar):
        if currentChar in Data.Eof.union({'\n'}):
            return CommentWithLookahead()
        
        return self
    

class State6(State):
    def next_state(self, currentChar):
        if currentChar in Data.star:
            return State7()
        if currentChar in Data.Eof:
            return UnclosedCommentErrorState()
        return self


class State7(State):
    def next_state(self, currentChar):
        if currentChar in Data.star:
            return self
        if currentChar in Data.slash:
            return CommentWithoutLookahead()
        if currentChar in Data.Eof:
            return UnclosedCommentErrorState()
        return State6()
    

class State8(State):
    def next_state(self, currentChar):
        if currentChar in Data.slash:
            return UnmatchedCommentErrorState()
        if currentChar in Data.validChars:
            return SymbolWithLookahead()
        return InvalidInputErrorState()


class CommentWithLookahead(LastState):
    def get_token_type(self):
        return "COMMENT"

    def is_lookahead(self):
        return True

class CommentWithoutLookahead(LastState):
    def get_token_type(self):
        return "COMMENT"

    def is_lookahead(self):
        return False
    
    
class NumberState(LastState):
    def get_token_type(self):
        return "NUM"

    def is_lookahead(self):
        return True
    

class WhiteSpace(LastState):
    def get_token_type(self):
        return "whiteSpace"

    def is_lookahead(self):
        return False
    

class Identifier(LastState):
    def get_token_type(self):
        return "ID"
    
    def is_lookahead(self):
        return True


class SymbolWithoutLookahead(LastState):
    def get_token_type(self):
        return "SYMBOL"
    def is_lookahead(self):
        return False

class SymbolWithLookahead(LastState):
    def get_token_type(self):
        return "SYMBOL"
    def is_lookahead(self):
        return True


class InvalidNumberErrorState(ErrorState):
    
    def __init__(self):
        self.isFinish = False

    def is_finish(self):
        return self.isFinish
    
    def next_state(self, currentChar):
        if currentChar in Data.letters:
            self.isFinish = False
        self.isFinish = True
    
    def is_lookahead(self):
        return True

    def get_error_type(self):
        return 'Invalid number'
    

class InvalidInputErrorState(ErrorState):

    def __init__(self):
        self.isFinish = False
        
    def is_finish(self):
        return self.isFinish
    
    def next_state(self, currentChar):
        self.isFinish = True
    
    def is_lookahead(self):
        return True
    
    def get_error_type(self):
        return "Invalid input"
    

class UnclosedCommentErrorState(ErrorState):
    
    def __init__(self):
        self.isFinish = True
        
    def is_finish(self):
        return self.isFinish
    
    def next_state(self, currentChar):
        pass

    def is_lookahead(self):
        return False
    
    def get_error_type(self):
        return "Unclosed comment"
    

class UnmatchedCommentErrorState(ErrorState):
    
    def __init__(self):
        self.isFinish = True
        
    def is_finish(self):
        return self.isFinish
    
    def next_state(self, currentChar):
        pass

    def is_lookahead(self):
        return False
    
    def get_error_type(self):
        return "Unmatched comment"

class Scanner:

    def __init__(self):
        self.data = Data()
        file_code = open("input.txt", "r")
        self.code = file_code.read()
        file_code.close()
        
        self.errors = []
        self.symbol_table = set(Data.keywords)
        self.lineNumber = 1
        self.currentIndex = 0
        self.lastIndex = len(self.code)


    def get_next_token(self):

        
        if self.lastIndex <= self.currentIndex:
            return ('file end', 'file ended', '┤', self.lineNumber)
        
        state = FirstState()
        initialCurrentIndex = self.currentIndex

        while True:
            if self.currentIndex < self.lastIndex:
                currentChar = self.code[self.currentIndex] 
            elif self.currentIndex == self.lastIndex:
                currentChar = None
            else:
                return ('file end', 'file ended', '┤', self.lineNumber)

            if isinstance(state, ErrorState):
                state.next_state(currentChar)
            else:        
                state = state.next_state(currentChar)

            if isinstance(state, LastState):
                if state.is_lookahead():
                    self.currentIndex -= 1

                if isinstance(state, WhiteSpace) and currentChar == '\n':
                    self.lineNumber += 1
                
                result = ('lastState', state.get_token_type())
                break

            if isinstance(state, ErrorState):
                if state.is_finish():
                    if state.is_lookahead():
                        self.currentIndex -= 1

                    result = ('errorState', state.get_error_type())
                    break
            
            if currentChar in Data.Eof:
                raise Exception("end of file reached invalidly")
            self.currentIndex += 1
        
        self.currentIndex += 1

        tokenToReturn = (result[0], result[1], self.code[initialCurrentIndex : self.currentIndex], self.lineNumber)

        if tokenToReturn[0]  == "lastState":
            if tokenToReturn[1] == 'whiteSpace' or tokenToReturn[1] == 'COMMENT':
                return self.get_next_token()
            else:
                if tokenToReturn[1] == 'ID':
                    self.symbol_table.add(tokenToReturn[2])
                if  tokenToReturn[2] in Data.keywords:
                    tokenToReturn = (tokenToReturn[0], 'KEYWORD', tokenToReturn[2], tokenToReturn[3])
        
        elif tokenToReturn[0] == "errorState":
            if tokenToReturn[1] == 'Unclosed comment':
                tokenToReturn = tokenToReturn[0], tokenToReturn[1], f'{tokenToReturn[2][0:min(7, len(tokenToReturn[2]))]}...', tokenToReturn[3]
            self.errors.append(tokenToReturn)
        else:
            raise Exception("invalid operation")

        # print(tokenToReturn)
        return tokenToReturn



parse_table = {"Program": [-1, -1, -1, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1], "DeclarationList": [2, 2, -1, 2, -1, 2, -1, 1, 1, -1, 2, 2, 2, 2, -1, 2, 2, -1, -1, -1, 2, 2, -1, 2, -1], "Declaration": ["synch", "synch", -1, "synch", -1, "synch", -1, 3, 3, -1, "synch", "synch", "synch", "synch", -1, "synch", "synch", -1, -1, -1, "synch", "synch", -1, "synch", -1], "DeclarationInitial": [-1, "synch", "synch", -1, -1, "synch", "synch", 4, 4, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "DeclarationPrime": ["synch", 6, 6, "synch", -1, 5, -1, "synch", "synch", -1, "synch", "synch", "synch", "synch", -1, "synch", "synch", -1, -1, -1, "synch", "synch", -1, "synch", -1], "VarDeclarationPrime": ["synch", 7, 8, "synch", -1, "synch", -1, "synch", "synch", -1, "synch", "synch", "synch", "synch", -1, "synch", "synch", -1, -1, -1, "synch", "synch", -1, "synch", -1], "FunDeclarationPrime": ["synch", "synch", -1, "synch", -1, 9, -1, "synch", "synch", -1, "synch", "synch", "synch", "synch", -1, "synch", "synch", -1, -1, -1, "synch", "synch", -1, "synch", -1], "TypeSpecifier": ["synch", -1, -1, -1, -1, -1, -1, 10, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "Params": [-1, -1, -1, -1, -1, -1, "synch", 12, 13, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "ParamList": [-1, -1, -1, -1, -1, -1, 15, -1, -1, 14, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "Param": [-1, -1, -1, -1, -1, -1, "synch", 16, 16, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "ParamPrime": [-1, -1, 17, -1, -1, -1, 18, -1, -1, 18, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "CompoundStmt": ["synch", "synch", -1, "synch", -1, "synch", -1, "synch", "synch", -1, 19, "synch", "synch", "synch", "synch", "synch", "synch", -1, -1, -1, "synch", "synch", -1, "synch", -1], "StatementList": [20, 20, -1, 20, -1, 20, -1, -1, -1, -1, 20, 21, 20, 20, -1, 20, 20, -1, -1, -1, 20, 20, -1, -1, -1], "Statement": [22, 22, -1, 22, -1, 22, -1, -1, -1, -1, 23, "synch", 22, 24, "synch", 25, 26, -1, -1, -1, 22, 22, -1, -1, -1], "ExpressionStmt": [27, 29, -1, 27, -1, 27, -1, -1, -1, -1, "synch", "synch", 28, "synch", "synch", "synch", "synch", -1, -1, -1, 27, 27, -1, -1, -1], "SelectionStmt": ["synch", "synch", -1, "synch", -1, "synch", -1, -1, -1, -1, "synch", "synch", "synch", 30, "synch", "synch", "synch", -1, -1, -1, "synch", "synch", -1, -1, -1], "IterationStmt": ["synch", "synch", -1, "synch", -1, "synch", -1, -1, -1, -1, "synch", "synch", "synch", "synch", "synch", 31, "synch", -1, -1, -1, "synch", "synch", -1, -1, -1], "ReturnStmt": ["synch", "synch", -1, "synch", -1, "synch", -1, -1, -1, -1, "synch", "synch", "synch", "synch", "synch", "synch", 32, -1, -1, -1, "synch", "synch", -1, -1, -1], "ReturnStmtPrime": [34, 33, -1, 34, -1, 34, -1, -1, -1, -1, "synch", "synch", "synch", "synch", "synch", "synch", "synch", -1, -1, -1, 34, 34, -1, -1, -1], "Expression": [36, "synch", -1, 35, "synch", 35, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 35, 35, -1, -1, -1], "B": [-1, 39, 38, -1, 39, 39, 39, -1, -1, 39, -1, -1, -1, -1, -1, -1, -1, 37, 39, 39, 39, 39, 39, -1, -1], "H": [-1, 41, -1, -1, 41, -1, 41, -1, -1, 41, -1, -1, -1, -1, -1, -1, -1, 40, 41, 41, 41, 41, 41, -1, -1], "SimpleExpressionZegond": [-1, "synch", -1, 42, "synch", 42, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 42, 42, -1, -1, -1], "SimpleExpressionPrime": [-1, 43, -1, -1, 43, 43, 43, -1, -1, 43, -1, -1, -1, -1, -1, -1, -1, -1, 43, 43, 43, 43, 43, -1, -1], "C": [-1, 45, -1, -1, 45, -1, 45, -1, -1, 45, -1, -1, -1, -1, -1, -1, -1, -1, 44, 44, -1, -1, -1, -1, -1], "Relop": ["synch", -1, -1, "synch", -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 46, 47, "synch", "synch", -1, -1, -1], "AdditiveExpression": [48, "synch", -1, 48, "synch", 48, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 48, 48, -1, -1, -1], "AdditiveExpressionPrime": [-1, 49, -1, -1, 49, 49, 49, -1, -1, 49, -1, -1, -1, -1, -1, -1, -1, -1, 49, 49, 49, 49, 49, -1, -1], "AdditiveExpressionZegond": [-1, "synch", -1, 50, "synch", 50, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, "synch", "synch", 50, 50, -1, -1, -1], "D": [-1, 52, -1, -1, 52, -1, 52, -1, -1, 52, -1, -1, -1, -1, -1, -1, -1, -1, 52, 52, 51, 51, -1, -1, -1], "Addop": ["synch", -1, -1, "synch", -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 53, 54, -1, -1, -1], "Term": [55, "synch", -1, 55, "synch", 55, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, "synch", "synch", 55, 55, -1, -1, -1], "TermPrime": [-1, 56, -1, -1, 56, 56, 56, -1, -1, 56, -1, -1, -1, -1, -1, -1, -1, -1, 56, 56, 56, 56, 56, -1, -1], "TermZegond": [-1, "synch", -1, 57, "synch", 57, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, "synch", "synch", 57, 57, -1, -1, -1], "G": [-1, 59, -1, -1, 59, -1, 59, -1, -1, 59, -1, -1, -1, -1, -1, -1, -1, -1, 59, 59, 59, 59, 58, -1, -1], "SignedFactor": [62, "synch", -1, 62, "synch", 62, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, "synch", "synch", 60, 61, "synch", -1, -1], "SignedFactorPrime": [-1, 63, -1, -1, 63, 63, 63, -1, -1, 63, -1, -1, -1, -1, -1, -1, -1, -1, 63, 63, 63, 63, 63, -1, -1], "SignedFactorZegond": [-1, "synch", -1, 66, "synch", 66, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, "synch", "synch", 64, 65, "synch", -1, -1], "Factor": [68, "synch", -1, 69, "synch", 67, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, "synch", "synch", "synch", "synch", "synch", -1, -1], "VarCallPrime": [-1, 71, 71, -1, 71, 70, 71, -1, -1, 71, -1, -1, -1, -1, -1, -1, -1, -1, 71, 71, 71, 71, 71, -1, -1], "VarPrime": [-1, 73, 72, -1, 73, -1, 73, -1, -1, 73, -1, -1, -1, -1, -1, -1, -1, -1, 73, 73, 73, 73, 73, -1, -1], "FactorPrime": [-1, 75, -1, -1, 75, 74, 75, -1, -1, 75, -1, -1, -1, -1, -1, -1, -1, -1, 75, 75, 75, 75, 75, -1, -1], "FactorZegond": [-1, "synch", -1, 77, "synch", 76, "synch", -1, -1, "synch", -1, -1, -1, -1, -1, -1, -1, -1, "synch", "synch", "synch", "synch", "synch", -1, -1], "Args": [78, -1, -1, 78, -1, 78, 79, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 78, 78, -1, -1, -1], "ArgList": [80, -1, -1, 80, -1, 80, "synch", -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 80, 80, -1, -1, -1], "ArgListPrime": [-1, -1, -1, -1, -1, -1, 82, -1, -1, 81, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]}
instruction_rights = ["DeclarationList", "Declaration DeclarationList", "", "DeclarationInitial DeclarationPrime", "TypeSpecifier ID", "FunDeclarationPrime", "VarDeclarationPrime", ";", "[ NUM ] ;", "( Params ) CompoundStmt", "int", "void", "int ID ParamPrime ParamList", "void", ", Param ParamList", "", "DeclarationInitial ParamPrime", "[ ]", "", "{ DeclarationList StatementList }", "Statement StatementList", "", "ExpressionStmt", "CompoundStmt", "SelectionStmt", "IterationStmt", "ReturnStmt", "Expression ;", "break ;", ";", "if ( Expression ) Statement else Statement", "while ( Expression ) Statement", "return ReturnStmtPrime", ";", "Expression ;", "SimpleExpressionZegond", "ID B", "= Expression", "[ Expression ] H", "SimpleExpressionPrime", "= Expression", "G D C", "AdditiveExpressionZegond C", "AdditiveExpressionPrime C", "Relop AdditiveExpression", "", "<", "==", "Term D", "TermPrime D", "TermZegond D", "Addop Term D", "", "+", "-", "SignedFactor G", "SignedFactorPrime G", "SignedFactorZegond G", "* SignedFactor G", "", "+ Factor", "- Factor", "Factor", "FactorPrime", "+ Factor", "- Factor", "FactorZegond", "( Expression )", "ID VarCallPrime", "NUM", "( Args )", "VarPrime", "[ Expression ]", "", "( Args )", "", "( Expression )", "NUM", "ArgList", "", "Expression ArgListPrime", ", Expression ArgListPrime", ""]
headers = ['ID', ';', '[', 'NUM', ']', '(', ')', 'int', 'void', ',', '{', '}', 'break', 'if', 'else', 'while', 'return', '=', '<', '==', '+', '-', '*', '┤', '/']
headers = {headers[i]: i for i in range(0, len(headers))}

first_node = Node('Program')
first_node_ins = Node('-1')

stack = ['┤', first_node]
stack_ins = ['', first_node_ins]

scanner = Scanner()

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
    skip_token = False
    if popped == '┤':
        break
    if headers.__contains__(popped.name):
        if popped.name != token_value and popped.name != 'ID' and popped.name != 'NUM':
            syntax_errors.append((popped.name ,"missing" ,line_number))
            popped.parent = None
        else:
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
        if (not headers.__contains__(token_value)):
            temp_token_value = 'ID'
            if token_type == 'NUM':
                temp_token_value = token_type

        if token_value == "if":
            print()
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
            continue
        if(instruction_to_use == "synch"):
            syntax_errors.append( (popped.name, "missing", line_number) )
            popped.parent = None
            continue
        states = instruction_rights[instruction_to_use].split(' ')
        newStack = []
        for state in states:
            newStack.append(Node(state if state != '' else 'epsilon', parent=popped))

        
        newStack.reverse()
        for n in newStack:
            stack.append(n)


if invalid_end:
    while len(stack) > 1:
        n = stack.pop()
        n.parent = None

if not invalid_end:
    Node('$', parent=first_node)

f = open("parse_tree.txt", "w", encoding="utf-8")
s = ""
for pre, fill, node in RenderTree(first_node):
    s += "%s%s\n" % (pre, node.name)
f.write(s[:-1])
f.close()

Node('$', parent=first_node_ins)
f = open("syntax_errors.txt", "w", encoding="utf-8")
if not syntax_errors:
    f.write("There is no syntax error.")
else:
    f.writelines([f"#{error[2]} : syntax error, {error[1]} {error[0]}\n" for error in syntax_errors])

f.close()