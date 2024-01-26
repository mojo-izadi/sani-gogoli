class Code_gen:

    def __init__(self) -> None:
        self.ss = []
        self.PB = []
        self.last_free_temp_address = 500
        self.last_free_address = 100
        self.func_table = {}
        self.var_table = {}
        self.arr_table = {}
        self.current_func = None


    def gettemp(self):
        self.last_free_temp_address += 4
        return self.last_free_temp_address - 4

    def get_new_addr(self, size):
        self.last_free_address += 4*size
        return self.last_free_address - 4*size

    def add(self, token):
        op1 = self.ss.pop()
        op2 = self.ss.pop()
        temp = self.gettemp()
        self.PB.append(f'(ADD, {op1}, {op2}, {temp})')
        self.ss.append(temp)

    def save_addop(self, token):
        self.ss.append(token)
    
    def add_sub(self, token):
        op1 = self.ss.pop()
        opt = self.ss.pop()
        opt = 'ADD' if opt == '+' else 'SUB'
        op2 = self.ss.pop()
        temp = self.gettemp()
        self.PB.append(f'({opt}, {op1}, {op2}, {temp})')
        self.ss.append(temp)
    
    def mult(self, token):
        op1 = self.ss.pop()
        op2 = self.ss.pop()
        temp = self.gettemp()
        self.PB.append(f'(MULT, {op1}, {op2}, {temp})')
        self.ss.append(temp)
    
    def assign(self, token):
        tempValue = self.ss.pop()
        assignee = self.ss.pop()
        self.PB.append(f'(ASSIGN, {tempValue}, {assignee}, )')
        self.ss.append(tempValue)
    
    def save_type(self, token):
        self.ss.append(token)
    
    def save_token(self, token):
        self.ss.append(token)

    def define_var(self, token):
        name = self.ss.pop()
        type = self.ss.pop()
        address = self.get_new_addr(1)
        self.var_table[name] = address
    
    def define_arr(self, token):
        name = self.ss.pop()
        type = self.ss.pop()
        address = self.get_new_addr(token)
        self.arr_table[name] = (address, token)
    
    def define_func(self, token):
        name = self.ss.pop()
        type = self.ss.pop()
        # self.ss.append(name)
        self.current_func = name
        first_instruction_index = len(self.PB)
        return_address = self.gettemp()
        return_value_address = self.gettemp()
        self.func_table[name] = function_data(name, type, return_address, return_value_address, first_instruction_index)
      
    def define_param_var(self, token):
        param_name = self.ss.pop()
        type = self.ss.pop()
        address = self.get_new_addr(1)
        func_name = self.current_func
        self.func_table[func_name].add_param(param_data(param_name, address, False))
    
    def define_param_arr(self, token):
        param_name = self.ss.pop()
        type = self.ss.pop()
        address = self.get_new_addr(1)
        func_name = self.current_func
        self.func_table[func_name].add_param(param_data(param_name, address, True))
    
    def end_func_body(self, token):
        self.var_table = {}
        self.arr_table = {}
        func_name = self.current_func
        self.PB.append(f'(JP, @{self.func_table[func_name].return_address}, , )')
        self.current_func = None
    
    def set_return_value(self, token):
        return_value = self.ss.pop()
        func_name = self.current_func
        self.PB.append(f'(ASSIGN, {return_value}, {self.func_table[func_name].return_value}, )')
    
    def return_control(self, token):
        func_name = self.current_func
        self.PB.append(f'(JP, @{self.func_table[func_name].return_address}, , )')
    

class function_data:
    def __init__(self, name, return_type, return_address, return_value_address, first_instruction_index):
        self.params = []
        self.name = name
        self.return_type = return_type
        self.return_address = return_address
        self.return_value_address = return_value_address
        self.first_instruction_index = first_instruction_index

    def add_param(self, param_data):
        self.params.append(param_data)

class param_data:
    def __init__(self, name, address, is_array) -> None:
        self.name = name
        self.address = address
        self.is_array = is_array