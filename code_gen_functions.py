class Code_gen:

    def __init__(self) -> None:
        self.ss = []
        self.ts = []
        self.PB = ['']
        self.last_free_temp_address = 500
        self.last_free_address = 100
        self.func_table = {}
        self.var_table = {}
        self.arr_table = {}
        self.global_var_table = {}
        self.global_arr_table = {}
        self.current_func = None
        self.calling_functions_stack = []
        self.while_depth = 0


    def gettemp(self):
        self.last_free_temp_address += 4
        return self.last_free_temp_address - 4

    def get_new_addr(self, size):
        self.last_free_address += 4*size
        return self.last_free_address - 4*size

    def save_num(self, token):
        temp = self.gettemp()
        self.PB.append(f'(ASSIGN, #{token}, {temp}, )')
        self.ss.append(temp)
        self.ts.append('int')

        
    def save_addop(self, token):
        self.ss.append(token)
        self.ts.append('')
    
    def add_sub(self, token):
        op1 = self.ss.pop()
        opt = self.ss.pop()
        opt = 'ADD' if opt == '+' else 'SUB'
        op2 = self.ss.pop()
        t1 = self.ts.pop()
        self.ts.pop()
        t2 = self.ts.pop()
        temp = self.gettemp()
        self.PB.append(f'({opt}, {op2}, {op1}, {temp})')
        self.ss.append(temp)
        self.ts.append('int')
        if t1 == 'array' or t2 == 'array':
            return Error('Type mismatch in operands, Got array instead of int')

    def relop(self, token):
        op1 = self.ss.pop()
        opt = self.ss.pop()
        opt = 'EQ' if opt == '==' else 'LT'
        op2 = self.ss.pop()
        t1 = self.ts.pop()
        self.ts.pop()
        t2 = self.ts.pop()
        temp = self.gettemp()
        self.PB.append(f'({opt}, {op2}, {op1}, {temp})')
        self.ss.append(temp)
        self.ts.append('int')
        if t1 == 'array' or t2 == 'array':
            return Error('Type mismatch in operands, Got array instead of int')
    
    def mult(self, token):
        op1 = self.ss.pop()
        op2 = self.ss.pop()
        t1 = self.ts.pop()
        t2 = self.ts.pop()
        temp = self.gettemp()
        self.PB.append(f'(MULT, {op1}, {op2}, {temp})')
        self.ss.append(temp)
        self.ts.append('int')
        if t1 == 'array' or t2 == 'array':
            return Error('Type mismatch in operands, Got array instead of int')
    
    def assign(self, token):
        tempValue = self.ss.pop()
        name = self.ss.pop()
        t1 = self.ts.pop()
        t2 = self.ts.pop()
        if name in self.var_table:
            assignee = self.var_table[name]
        elif name in self.global_var_table:
            assignee = self.global_var_table[name]
        else:
            self.ss.append(tempValue)
            self.ts.append('int')
            return Error(f'\'{name}\' is not defined')
        self.PB.append(f'(ASSIGN, {tempValue}, {assignee}, )')
        self.ss.append(tempValue)
        self.ts.append('int')
        if t1 != t2:
            return Error(f'Type mismatch in operands, Got {t2} instead of {t1}')
    
    def assign_arr(self, token):
        tempValue = self.ss.pop()
        assignee = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        self.PB.append(f'(ASSIGN, {tempValue}, @{assignee}, )')
        self.ss.append(tempValue)
        self.ts.append('int')
    
    def save_type(self, token):
        self.ss.append(token)
        self.ts.append('')
    
    def save_token(self, token):
        self.ss.append(token)
        self.ts.append('')

    def define_var(self, token):
        name = self.ss.pop()
        type = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        address = self.get_new_addr(1)
        if type == 'void':
            self.var_table[name] = address
            return Error(f'Illegal type of void for \'{name}\'')
        if self.current_func:
            self.var_table[name] = address
        else:
            self.global_var_table[name] = address
    
    def define_arr(self, token):
        name = self.ss.pop()
        type = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        address = self.get_new_addr(int(token))
        if type == 'void':
            self.arr_table[name] = (address, token)
            return Error(f'Illegal type of void for \'{name}\'')
        if self.current_func:
            self.arr_table[name] = (address, token)
        else:
            self.global_arr_table[name] = (address, token)
    
    def define_func(self, token):
        name = self.ss.pop()
        type = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        self.current_func = name
        first_instruction_index = len(self.PB)
        return_address = self.gettemp()
        return_value_address = self.gettemp()
        self.PB.append(f'(ASSIGN, #0, {return_value_address}, )')
        self.func_table[name] = function_data(name, type, return_address, return_value_address, first_instruction_index)
        if name == 'main':
            self.PB[0] = f'(JP, {first_instruction_index}, , )'
      
    def define_param_var(self, token):
        param_name = self.ss.pop()
        type = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        address = self.get_new_addr(1)
        func_name = self.current_func
        self.func_table[func_name].add_param(param_data(param_name, address, False))
    
    def define_param_arr(self, token):
        param_name = self.ss.pop()
        type = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
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
        self.ts.pop()
        func_name = self.current_func
        self.PB.append(f'(ASSIGN, {return_value}, {self.func_table[func_name].return_value_address}, )')
    
    def return_control(self, token):
        func_name = self.current_func
        self.PB.append(f'(JP, @{self.func_table[func_name].return_address}, , )')
    
    def save_index_address(self, token):
        index_temp = self.ss.pop()
        array_id = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        temp = self.gettemp()
        initial_len = len(self.PB)

        if array_id in self.arr_table:
            self.PB.append(f'(ADD, {index_temp}, #{self.arr_table[array_id][0]}, {temp})')
            self.ss.append(temp)
            self.ts.append('int')
            return
        
        for param in self.func_table[self.current_func].params:
            if param.name == array_id and param.is_array:
                self.PB.append(f'(ADD, {index_temp}, {param.address}, {temp})')
                self.ss.append(temp)
                self.ts.append('int')
                return
        
        if array_id in self.global_arr_table:
            self.PB.append(f'(ADD, {index_temp}, #{self.global_arr_table[array_id][0]}, {temp})')
            self.ss.append(temp)
            self.ts.append('int')
            return
        
        if initial_len == len(self.PB):
            self.ss.append(1)
            self.ss.append(1)
            self.ts.append('')
            self.ts.append('')
            return Error(f'\'{array_id}\' is not defined')

    
    def save_index_value(self, token):
        temp = self.gettemp()
        index_addr = self.ss.pop()
        self.ts.pop()
        self.PB.append(f'(ASSIGN, @{index_addr}, {temp}, )')
        self.ss.append(temp)
        self.ts.append('int')
    
    def save_id(self, token):
        self.ss.append(token)
        if token in self.var_table or token in self.global_var_table:
            self.ts.append('int')
        elif token in self.arr_table or token in self.global_arr_table:
            self.ts.append('array')
        else:
            self.ts.append('')

    def push_id_value(self, token):
        id = self.ss.pop()
        self.ts.pop()
        
        if id in self.var_table:
            var_addr = self.var_table[id]
            self.ss.append(var_addr)
            self.ts.append('int')
            return

        if id in self.arr_table:
            arr_data = self.arr_table[id]
            self.ss.append(arr_data[0])
            self.ts.append('array')
            return
        
        for param in self.func_table[self.current_func].params:
            if param.name == id:
                self.ss.append(param.address)
                self.ts.append('array' if param.is_array else 'int')
                return
        
        if id in self.global_var_table:
            var_addr = self.global_var_table[id]
            self.ss.append(var_addr)
            self.ts.append('int')
            return
        
        if id in self.global_arr_table:
            arr_data = self.global_arr_table[id]
            self.ss.append(arr_data[0])
            self.ts.append('array')
            return
        
        self.ss.append(1)
        self.ts.append('')
        return Error(f'\'{id}\' is not defined')


    def start_call(self, token):
        func_id = self.ss.pop()
        self.ts.pop()
        self.calling_functions_stack.append(func_id)
        if func_id == self.current_func:
            exit(1)
        self.ss.append('1c')
        self.ts.append('')

    def end_func_call(self, token):
        error = None
        calling_function_id = self.calling_functions_stack.pop()
        if calling_function_id == 'output':
            if self.ss[-2] != '1c':
                return Error(f'Mismatch in numbers of arguments of \'output\'')
            self.PB.append(f'(PRINT, {self.ss.pop()}, , )')
            self.ss.pop()
            self.ts.pop()
            self.ts.pop()
            self.ss.append('dummy')
            self.ts.append('')
            return
        if calling_function_id not in self.func_table:
            return Error(f'\'{calling_function_id}\' is not defined')
        func_data = self.func_table[calling_function_id]
        func_params = func_data.params
        func_params = func_params.copy()
        func_params.reverse()
        for i in range(len(func_params)):
            func_param = func_params[i]
            param_temp = self.ss.pop()
            proposed_param_type = self.ts.pop()
            if param_temp == '1c':
                self.ss.append(123)
                self.ts.append('int')
                return Error(f'Mismatch in numbers of arguments of \'{calling_function_id}\'')
            if func_param.is_array:
                if proposed_param_type == 'int':
                    error = Error(f'Mismatch in type of argument {i + 1} of \'{calling_function_id}\'. Expected \'array\' but got \'int\' instead')
                self.PB.append(f'(ASSIGN, #{param_temp}, {func_param.address}, )')
            else:
                if proposed_param_type == 'array':
                    error = Error(f'Mismatch in type of argument {i + 1} of \'{calling_function_id}\'. Expected \'int\' but got \'array\' instead')
                self.PB.append(f'(ASSIGN, {param_temp}, {func_param.address}, )')
        
        top = self.ss.pop()
        self.ts.pop()
        if top != '1c':
            while top != '1c':
                top = self.ss.pop()
                self.ts.pop()
            temp = self.gettemp()
            self.ss.append(temp)
            self.ts.append('int')
            return Error(f'Mismatch in numbers of arguments of \'{calling_function_id}\'')
        self.PB.append(f'(ASSIGN, #{len(self.PB) + 2}, {func_data.return_address}, )')
        self.PB.append(f'(JP, {func_data.first_instruction_index}, , )')

        temp = self.gettemp()
        self.PB.append(f'(ASSIGN, {func_data.return_value_address}, {temp}, )')
        self.ss.append(temp)
        self.ts.append('int')
        if error:
            return error
        
        
    
    def label(self, token):
        temp = self.gettemp()
        self.PB.append('')
        self.ss.append(temp)
        self.ss.append(len(self.PB))
        self.ts.append('int')
        self.ts.append('')
        self.while_depth += 1
    
    def save(self, token):
        self.ss.append(len(self.PB))
        self.ts.append('')
        self.PB.append('')
    
    def save_if(self, token):
        self.ss.append(len(self.PB))
        self.ss.append('1i')
        self.ts.append('')
        self.ts.append('')
        self.PB.append('')
    
    def end_while(self, token):
        condition_end_addr = self.ss.pop()
        condition_value = self.ss.pop()
        while_start_addr = self.ss.pop()
        condition_end_line_addr = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        self.ts.pop()
        self.ts.pop()
        self.PB.append(f'(JP, {while_start_addr}, , )')
        self.PB[while_start_addr - 1] = f'(ASSIGN, #{len(self.PB)}, {condition_end_line_addr}, )'
        self.PB[condition_end_addr] = f'(JPF, {condition_value}, {len(self.PB)}, )'
        self.while_depth -= 1
    
    def break_action(self, token):
        if self.while_depth == 0:
            return Error("No 'while' found for 'break'")
        ss_top = -1
        break_addr = -4
        while True:
            if self.ss[ss_top] == '1e':
                break_addr -= 2
                ss_top -= 2
            elif self.ss[ss_top] == '1i':
                break_addr -= 3
                ss_top -= 3
            else:
                break

        self.PB.append(f'(JP, @{self.ss[break_addr]}, , )')

        
    def remove_assigned(self, token):
        self.ts.pop()
        self.ss.pop()


    def jpf_save(self, token):
        self.ss.pop() #pop 1i
        if_start = self.ss.pop()
        condition_value = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        self.ts.pop()
        self.ss.append(len(self.PB))
        self.ss.append('1e')
        self.ts.append('')
        self.ts.append('')
        self.PB.append('')
        self.PB[if_start] = f'(JPF, {condition_value}, {len(self.PB)}, )'
    
    def jp(self, token):
        self.ss.pop() # 1e
        condition_addr = self.ss.pop()
        self.ts.pop()
        self.ts.pop()
        self.PB[condition_addr] = f'(JP, {len(self.PB)}, , )'
        
        
                

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

class Error:
    def __init__(self, message) -> None:
        self.message = message