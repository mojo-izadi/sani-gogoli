import string

code = open("./input.txt", "r")

numbers = set(range(0, 10))
letters = set(string.ascii_letters)
alphanumeric = numbers.union(letters)
whitespace = set(string.whitespace)
symbols = {';', ':', ',', '(', ')', '{', '}', '[', ']', '+', '-', '<', '>'}
equalSymbol = {'='}
slash = {'/'}
star = {'*'}
Eof = {'fuck you because im end of file'}

validChars = alphanumeric.union(whitespace)\
    .union(symbols).union(equalSymbol).union(slash).union(star).union(Eof)

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
    def error_finish():
        pass

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
            return SymbolWithoutLookahead()
        if currentChar in equalSymbol:
            return State3()
        if currentChar in slash:
            return State4()
        if currentChar in whitespace:
            return WhiteSpace()
        if currentChar in star:
            return State8()
        

class State1(State):
    def next_state(self, currentChar):
        if currentChar in numbers:
            return self
        if currentChar in letters:
            return InvalidNumberErrorState()
        else:
            return NumberState()
        

class State2(State):
    def next_state(self, currentChar):
        if currentChar in alphanumeric:
            return self
        if currentChar in validChars:
            return Identifier()
        else:
            return InvalidInputErrorState()
        

class State3(State):
    def next_state(self, currentChar):
        if currentChar in equalSymbol:
            return SymbolWithoutLookahead()
        return SymbolWithLookahead()
    

class State4(State):
    def next_state(self, currentChar):
        if currentChar in slash:
            return State5()
        if currentChar in star:
            return State6()
        return SymbolWithLookahead()
    

class State5(State):
    def next_state(self, currentChar):
        if currentChar in Eof.union({'\n'}):
            return CommentWithLookahead()
        
        return self
    

class State6(State):
    def next_state(self, currentChar):
        if currentChar in star:
            return State7()
        if currentChar in Eof:
            return UnclosedCommentErrorState()
        return self


class State7(State):
    def next_state(self, currentChar):
        if currentChar in star:
            return self
        if currentChar in slash:
            return CommentWithoutLookahead()
        if currentChar in Eof:
            return UnclosedCommentErrorState()
        return State6()
    

class State8(State):
    def next_state(self, currentChar):
        if currentChar in slash:
            return UnmatchedCommentErrorState()
        return SymbolWithLookahead()


class CommentWithLookahead(LastState):
    def get_token_type(self):
        "comment"

    def is_lookahead(self):
        return True

class CommentWithoutLookahead(LastState):
    def get_token_type(self):
        "comment"

    def is_lookahead(self):
        return False
    
    
class NumberState(LastState):
    def get_token_type(self):
        return "number"

    def is_lookahead(self):
        return True
    

class WhiteSpace(LastState):
    def get_token_type(self):
        return "whiteSpace"

    def is_lookahead(self):
        return False
    

class Identifier(LastState):
    def get_token_type(self):
        return "Identifier"
    
    def is_lookahead(self):
        True


class SymbolWithoutLookahead(LastState):
    def get_token_type(self):
        "Symbol"
    def is_lookahead(self):
        False

class SymbolWithLookahead(LastState):
    def get_token_type(self):
        "Symbol"
    def is_lookahead(self):
        True


class InvalidNumberErrorState(ErrorState):
    
    def error_finish():
        return False
    
    def error_finish(currentChar):
        if currentChar in letters:
            return False
        return True
    
    def get_error_type(self):
        return 'Invalid number'
    

class InvalidInputErrorState(ErrorState):

    def error_finish():
        return False
    
    def error_finish(currentChar):
        return currentChar in validChars

    def get_error_type(self):
        return "Invalid input"
    

class UnclosedCommentErrorState(ErrorState):
    
    def error_finish():
        return True
    
    def error_finish(currentChar):
        return True

    def get_error_type(self):
        return "Unclosed comment"
    

class UnmatchedCommentErrorState(ErrorState):
    
    def error_finish():
        return True
    
    def error_finish(currentChar):
        return True

    def get_error_type(self):
        return "Unmatched comment"