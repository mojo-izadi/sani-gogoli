import string

code = open("./input.txt", "r")

numbers = set(range(0, 10))
letters = set(string.ascii_letters)
alphanumeric = numbers.union(letters)
whitespace = set(string.whitespace)
symbols = {';', ':', ',', '(', ')', '{', '}', '[', ']', '+', '-', '*', '<', '>'}
equalSymbol = {'='}

currentIndex = 0


def get_next_token():
    global currentIndex
    while True:
        currentChar = code[currentIndex]

        currentIndex += 1


class State:
    def next_state(self, currentChar):
        pass


class LastState(State):
    def next_state(self, currentChar):
        raise Exception('fucked up')

    def get_token_type(self):
        pass

    def is_lookahead(self):
        pass


class ErrorState(State):

    def get_error_text(self):
        pass

    def is_last_error_state(self):
        pass


class NumberState(LastState):
    def get_token_type(self):
        return "number"

    def is_lookahead(self):
        return True


class FirstState(State):
    def next_state(self, currentChar):
        if currentChar in numbers:
            return State1()


class State1(State):
    def next_state(self, currentChar):
        if currentChar in numbers:
            return State1()
        if currentChar in letters:
            return ErrorState1()
        else:
            return NumberState()


class ErrorState1(ErrorState):

    def __init__(self, is_last_error_state):
        self.is_last_error_state = is_last_error_state

    def get_error_text(self):
        return 'number error'

    def is_last_error_state(self):
        return self.is_last_error_state

    def next_state(self, currentChar):
        if currentChar in letters:
            return ErrorState1(False)
        else:
            return ErrorState1(True)
