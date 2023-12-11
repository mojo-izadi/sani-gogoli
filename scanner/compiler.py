import string

file_code = open("./input.txt", "r")
code = file_code.read()
file_code.close()

numbers = set([str(i) for i in range(0, 10)])
letters = set(string.ascii_letters)
alphanumeric = numbers.union(letters)
whitespace = set(string.whitespace)
symbols = {';', ':', ',', '(', ')', '{', '}', '[', ']', '+', '-', '<', '>'}
equalSymbol = {'='}
slash = {'/'}
star = {'*'}
Eof = {None}

validChars = alphanumeric.union(whitespace) \
    .union(symbols).union(equalSymbol).union(slash).union(star).union(Eof)

lineNumber = 1
currentIndex = 0
lastIndex = len(code)


def get_next_token():
    global currentIndex, lastIndex, lineNumber

    if lastIndex <= currentIndex:
        return 'file ended'

    state = FirstState()
    initialCurrentIndex = currentIndex

    while True:
        if currentIndex < lastIndex:
            currentChar = code[currentIndex]
        elif currentIndex == lastIndex:
            currentChar = None
        else:
            return "file ended"

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

        if currentChar in Eof:
            raise Exception("end of file reached invalidly")
        currentIndex += 1

    currentIndex += 1
    return result[0], result[1], code[initialCurrentIndex: currentIndex], lineNumber


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
        return InvalidInputErrorState()


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
        # if currentChar in slash:
        #     return State5()
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
        if currentChar in validChars:
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
        if currentChar in letters:
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
        # self.isFinish = currentChar in validChars
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


keywords = {'if', 'else', 'void', 'int', 'while', 'break', 'return'}

nextToken = None
lastStates = []
errors = []
symbol_table = set(keywords)

while True:
    nextToken = get_next_token()
    if nextToken == "file ended":
        break
    if nextToken[0] == "lastState":
        if nextToken[1] != 'whiteSpace' and nextToken[1] != 'COMMENT':
            if nextToken[1] == 'ID':
                symbol_table.add(nextToken[2])
            lastStates.append(nextToken)

    elif nextToken[0] == "errorState":
        if nextToken[1] == 'Unclosed comment':
            nextToken = nextToken[0], nextToken[1], f'{nextToken[2][0:min(7, len(nextToken[2]))]}...', nextToken[3]
        errors.append(nextToken)
    else:
        raise Exception("invalid operation")
    # print(nextToken)


def prepare_output(stateReports, keyFirst):
    tokens = [[] for _ in range(0, lineNumber)]
    for lastState in stateReports:
        key = lastState[1]
        if lastState[2] in keywords:
            key = 'KEYWORD'
        if keyFirst:
            tokens[lastState[3] - 1].append(f'({key}, {lastState[2]})')
        else:
            tokens[lastState[3] - 1].append(f'({lastState[2]}, {key})')

    tokensToStore = []
    for i in range(0, len(tokens)):
        token = tokens[i]
        if len(token) == 0:
            continue
        tokensToStore.append(f'{i + 1}.\t{" ".join(token)}')

    return "\n".join(tokensToStore)


tokensToStoreStr = prepare_output(lastStates, True)
f = open("tokens.txt", "w")
f.write(tokensToStoreStr)
f.close()

symbol_table_list = list(symbol_table)

symbol_table_str = "\n".join([f'{i + 1}.\t{symbol_table_list[i]}' for i in range(0, len(symbol_table_list))])
f = open("symbol_table.txt", "w")
f.write(symbol_table_str)
f.close()

f = open("tokens.txt", "w")
f.write(tokensToStoreStr)
f.close()

f = open("lexical_errors.txt", "w")
if len(errors) == 0:
    errors_str = 'There is no lexical error.'
else:
    errors_str = prepare_output(errors, False)
f.write(errors_str)
f.close()
