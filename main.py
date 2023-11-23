import string

code = open("./input.txt", "r")

numbers = set(range(0, 10))
letters = set(string.ascii_letters)
alphanumeric = numbers.union(letters)
whitespace = set(string.whitespace)
symbols = {';', ':', ',', '(', ')', '{', '}', '[', ']', '+', '-', '*', '<', '>'}
equalSymbol = {'='}
slash = {'/'}
star = {'*'}

validChars = alphanumeric.union(whitespace).union(symbols).union(equalSymbol).union(slash)

currentIndex = 0


def get_next_token():
    global currentIndex
    while True:
        currentChar = code[currentIndex]
        #move state
        currentIndex += 1


class State:
    def next_state(self, currentChar):
        pass


class LastState():
    def get_token_type(self):
        pass

    def is_lookahead(self):
        pass


class ErrorState:

    def error_finish(currentChar):
        pass

    def get_error_type(self):
        pass
    

class FirstState(State):
    def next_state(self, currentChar):
        if currentChar in numbers:
            return State1()
        if currentChar in letters:
            return State2()
        if currentChar in symbols:
            return Symbol1()
        if currentChar in equalSymbol:
            return State3()
        if currentChar in slash:
            return State4()
        

class State1(State):
    def next_state(self, currentChar):
        if currentChar in numbers:
            return self
        if currentChar in letters:
            return ErrorState1()
        else:
            return NumberState()
        
    
class ErrorState1(ErrorState):

    def get_error_type(self):
        return 'Invalid number'

    def error_finish(currentChar):
        if currentChar in letters:
            return False
        return True

class NumberState(LastState):
    def get_token_type(self):
        return "number"

    def is_lookahead(self):
        return True
    


class State2(State):
    def next_state(self, currentChar):
        if currentChar in alphanumeric:
            return self
        if currentChar in validChars:
            return Identifier()
        else:
            return ErrorState2()

class ErrorState2(ErrorState):
    def error_finish(currentChar):
        return currentChar in validChars

    def get_error_type(self):
        return "Invalid input"

class Identifier(LastState):
    def get_token_type(self):
        return "Identifier"
    
    def is_lookahead(self):
        True


class Symbol1(LastState):
    def get_token_type(self):
        "Symbol"
    def is_lookahead(self):
        False

class Symbol2(LastState):
    def get_token_type(self):
        "Symbol"
    def is_lookahead(self):
        True


class State3(State):
    def next_state(self, currentChar):
        if currentChar in equalSymbol:
            return Symbol1()
        return Symbol2()
    
class State4(State):
    def next_state(self, currentChar):
        if currentChar in slash:
            return State5()
        if currentChar in star:
            return State6()
        return Symbol2()
    
class State5(State):
    def next_state(self, currentChar):
        if currentChar in slash:
            return Symbol1()
        return Symbol2()
    
class State6(State):
    def next_state(self, currentChar):
        if currentChar in slash:
            return Symbol1()
        return Symbol2()