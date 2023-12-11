import string


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
        if currentChar in Data.slash:
            return State5()
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
        return SymbolWithLookahead()


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
        self.isFinish = currentChar in Data.validChars
    
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
        file_code = open("P2_TestCases/T01/input.txt", "r")
        self.code = file_code.read()
        file_code.close()
        
        self.errors = []
        self.symbol_table = set(Data.keywords)

    def get_next_token(self):

        lineNumber = 1
        currentIndex = 0
        lastIndex = len(self.code)

        if lastIndex <= currentIndex:
            return ('file end', 'file ended', '┤', lineNumber)
        
        state = FirstState()
        initialCurrentIndex = currentIndex

        while True:
            if currentIndex < lastIndex:
                currentChar = self.code[currentIndex] 
            elif currentIndex == lastIndex:
                currentChar = None
            else:
                return ('file end', 'file ended', '┤', lineNumber)

            if isinstance(state, ErrorState):
                state.next_state(currentChar)
            else:        
                state = state.next_state(currentChar)

            if isinstance(state, LastState):
                if state.is_lookahead():
                    currentIndex -= 1

                if isinstance(state, WhiteSpace) and currentChar == '\n':
                    lineNumber += 1
                
                result = ('lastState', state.get_token_type())
                break

            if isinstance(state, ErrorState):
                if state.is_finish():
                    if state.is_lookahead():
                        currentIndex -= 1

                    result = ('errorState', state.get_error_type())
                    break
            
            if currentChar in Data.Eof:
                raise Exception("end of file reached invalidly")
            currentIndex += 1
        
        currentIndex += 1

        tokenToReturn = (result[0], result[1], self.code[initialCurrentIndex : currentIndex], lineNumber)

        if tokenToReturn[0]  == "lastState":
            if tokenToReturn[1] == 'whiteSpace':
                return self.get_next_token()
            else:
                if tokenToReturn[1] == 'ID':
                    self.symbol_table.add(tokenToReturn[2])
                if  tokenToReturn[2] in Data.keywords:
                    tokenToReturn[1] = 'KEYWORD'
            

        return tokenToReturn

    # while True:
    #     nextToken = get_next_token()
    #     if nextToken == "file ended":
    #         break

    #     if nextToken[0]  == "lastState":
    #         if nextToken[1] != 'whiteSpace':
    #             if nextToken[1] == 'ID':
    #                 symbol_table.add(nextToken[2])
    #             if  nextToken[2] in keywords:
    #                 nextToken[1] = 'KEYWORD'
    #             lastStates.append(nextToken)
    #             next_token
        

    #     elif nextToken[0]  == "errorState":
    #         errors.append(nextToken)
    #     else:
    #         raise Exception("invalid operation")
