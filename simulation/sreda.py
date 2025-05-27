from typing import List
import random

class Sreda:
    def __init__(self):
        self.sreda_a = 0 #climate cycle factor 1 [0,0.00125]
        self.sreda_b = 0 #climate cycle factor 2 [0,0.00125]
        self.sreda_c = 0.46 #energy random unfitorm 0.01 0.25 1.50
        self.sreda_d = 0.29 #energy random unfitorm 0.01 0.25 1.50
        self.sreda_e = 0.25 #energy random unfitorm 0.01 0.25 1.50
        self.sreda_f = 1 #energy factor [0.5,1.5]
        self.sreda_g = 0 #energy factor [0,1]
        self.sreda_h = 0 #energy random unfitorm +-0.01
        self.sreda_mutation_chance = 0.0015 # 0 to 0.01 
        self.sreda_feedback = [0] * 128 # 16 to 2048
        self.sreda_noise_seed = 42 #1 to 1025
        self.adaptability = 1

    def get_sreda_a(self):
        return self.sreda_a

    def get_sreda_b(self):
        return self.sreda_b

    def get_sreda_c(self):
        return self.sreda_c

    def get_sreda_d(self):
        return self.sreda_d

    def get_sreda_e(self):
        return self.sreda_e

    def get_sreda_f(self):
        return self.sreda_f
    
    def get_sreda_g(self):
        return self.sreda_g

    def get_sreda_h(self):
        return self.sreda_h
    
    def get_sreda_mutation_chance(self):
        return self.sreda_mutation_chance

    def get_sreda_random_seed(self):
        #random.seed(self.sreda_noise_seed)
        return random.random()
    
    def get_sreda_feedback(self):
        return self.sreda_feedback
    
    def modify_sreda_a(self, new_value):
        self.sreda_a = new_value
    
    def modify_sreda_a(self, new_value):
        self.sreda_a = new_value

    def modify_sreda_b(self, new_value):
        self.sreda_b = new_value
    
    def modify_sreda_c(self, new_value):
        self.sreda_c = new_value
    
    def modify_sreda_d(self, new_value):
        self.sreda_d = new_value
    
    def modify_sreda_e(self, new_value):
        self.sreda_e = new_value
    
    def modify_sreda_f(self, new_value):
        self.sreda_f = new_value
    
    def modify_sreda_g(self, new_value):
        self.sreda_g = new_value
    
    def modify_sreda_h(self, new_value):
        self.sreda_h = new_value

    def modify_sreda_mutation_chance(self, new_value):
        self.sreda_mutation_chance = new_value

    def modify_sreda_feedback(self, new_value):
        self.sreda_feedback = new_value

    def interact_with_enviroment_global(self, modified_values:List):
        self.adaptability+=1
        min_vals = [0,0,0.01,0.01,0.01,0.5,0,-0.01,0.0015,16]
        max_vals = [0.00125,0.00125,1.5,1.5,1.5,1.5,1,0.01,0.01,2048]

        lst = []
        
        for i in range(len(modified_values)):
            mv = (modified_values[i], 0, int(modified_values[i]*random.random()*5)+0.01, min_vals[i], max_vals[i])
            lst.append(self.normalize(*mv))
        
        self.sreda_a = (lst[0] + self.sreda_a)//2 
        self.sreda_b = (lst[1] + self.sreda_b)//2 
        self.sreda_c = (lst[2] + self.sreda_c)//2 
        self.sreda_d = (lst[3] + self.sreda_d)//2 
        self.sreda_e = (lst[4] + self.sreda_e)//2 
        self.sreda_f = (lst[5] + self.sreda_f)//2 
        self.sreda_g = (lst[6] + self.sreda_g)//2 
        self.sreda_h = (lst[7] + self.sreda_h)//2 
        self.sreda_mutation_chance = (lst[8] + self.sreda_mutation_chance)//2 
        self.sreda_feedback = self.sreda_feedback + [max(self.sreda_feedback) + self.sreda_mutation_chance]

    def sreda_update_biases(self,data):
        res = ""
        for el in data:
            if (el < 0):
                el = 0
            if (el >= 10):
                el = 9
            res+=str(int(el))

        return res
    
    def normalize(self,value, min_val, max_val, a=0, b=1):
        return a + (value - min_val) * (b - a) / (max_val - min_val)