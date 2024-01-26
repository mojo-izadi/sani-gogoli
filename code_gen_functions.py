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
        self.calling_functions_stack = []


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
    
    def assign_arr(self, token):
        tempValue = self.ss.pop()
        assignee = self.ss.pop()
        self.PB.append(f'(ASSIGN, {tempValue}, @{assignee}, )')
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
    
    def save_index_address(self, token):
        index_temp = self.ss.pop()
        array_id = self.ss.pop()
        temp = self.gettemp()

        if array_id in self.arr_table:
            self.PB.append(f'(ADD, {index_temp}, #{self.arr_table[array_id][0]}, {temp})')
            self.ss.append(temp)
        
        for param in self.func_table[self.current_func].params:
            if param.name == id and param.is_array:
                self.ss.append(param.address)
                self.PB.append(f'(ADD, {index_temp}, #{self.param.address}, {temp})')
                self.ss.append(temp)
                break

    
    def save_index_value(self, token):
        temp = self.gettemp()
        index_addr = self.ss.pop()
        self.PB.append(f'(ASSIGN, @{index_addr}, {temp}, )')
        self.ss.append(temp)
    
    def save_id(self, token):
        self.ss.append(token)

    def push_id_value(self, token):
        id = self.ss.pop()

        if id in self.var_table:
            var_addr = self.var_table[id]
            self.ss.append(var_addr)

        if id in self.arr_table:
            arr_data = self.arr_table[id]
            self.ss.append(arr_data[0])
        
        for param in self.func_table[self.current_func].params:
            if param.name == id:
                self.ss.append(param.address)
                break

    def start_call(self, token):
        func_id = self.ss.pop()
        self.calling_functions_stack.append(func_id)

    def end_func_call(self, token):
        calling_function_id = self.calling_functions_stack.pop()
        func_params = self.func_table[calling_function_id].params
        func_params = func_params.copy()
        func_params.reverse()
        for func_param in func_params:
            self.PB.append(f'(ASSIGN, {var_addr}, {temp}, )')

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