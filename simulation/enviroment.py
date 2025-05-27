import random
from graph import Graph
import json
import csv
from creature import Creature
from sreda import Sreda

class Enviroment:
    """
    The aim of the class is to distribute energy among the tiles of the simulation. There are 6200 tiles. An energy function,
    described in the project's architecture is implemented here.
    """
    def __init__(self, graph, trial_number):
        self.graph = graph
        self.time_of_day = 12 #quickest goes from [0 to 24)
        self.seasonal_cycle = 1.0 #medium goes from [0 -> 1 -> 2 -> 3] WSSA Winter, spring, summer autumn
        self.climate_cycle = 5.0 #longest fluctuates from [0 to 10)
        self.trend = 1
        self.size = 1620
        self.turn_number = 0
        self.trial_number = trial_number
        self.sreda = Sreda()
        
    def turn_update(self, sreda_a = 0, sreda_b = 0):
        self.time_of_day += 1
        if (self.time_of_day >= 24):
            self.time_of_day = 0
        
        self.seasonal_cycle += 1/(24*90)
        if (self.seasonal_cycle >= 4):
            self.seasonal_cycle = 0

        self.climate_cycle += (random.random() * (0.002 + sreda_a)) - (0.001 + sreda_b) + self.trend/(24*90*12)

        if (self.climate_cycle < 0):
            self.climate_cycle = 0.0
            self.trend = 1
        elif (self.climate_cycle > 10):
            self.climate_cycle = 10
            self.trend = -1

        #print(self.climate_cycle, self.seasonal_cycle, self.time_of_day)

    def energy_function(self, sreda_c = 0.46, sreda_d = 0.29, sreda_e = 0.25, sreda_f = 1, sreda_g = 0, sreda_h = random.uniform(-0.01,0.01)):
        #we calculate how much power is to be given out based on the enviroment.
        total_power = (abs(self.time_of_day - 12) * sreda_c + abs(self.climate_cycle - 2) * sreda_d + self.climate_cycle * sreda_e) * self.size * sreda_f + sreda_g
        if (total_power < 0):
            total_power = 0

        #we distribute the energy among tiles
        north_share = 0
        south_share = 0

        if (abs(self.seasonal_cycle - 2) < 1):
            north_share = 0.75
            south_share = 0.25
        elif (abs(self.seasonal_cycle - 1) < 1  or abs(self.seasonal_cycle - 3) < 1):
            north_share = 0.5
            south_share = 0.5
        else:
            north_share = 0.25
            south_share = 0.75
        
        #sreda h must be < 0.25 NOte

        north_share += sreda_h
        south_share -= sreda_h

        north_share = total_power * north_share
        south_share = total_power * south_share

        return north_share, south_share

    def distribute(self, north_share, south_share):
        lst = []

        s = [random.random() for j in range(self.size//2)]
        t = sum(s)

        lst_temp1 = [north_share * weight for weight in [q / t for q in s]]

        s = [random.random() for j in range(self.size//2)]
        t = sum(s)
        lst_temp2 = [south_share * weight for weight in [q / t for q in s]]

        lst = lst_temp1 + lst_temp2

        return lst

    def add_creature(self, creature):
        graph.set_state(creature.location, creature)

    def get_neightbours(self, location):
        return graph.get_n(location)
    
    def next_turn(self):
        self.turn_number+=1

        mean_creature_feedback = [0]*10 #avegeded result of feedback of every lingle creature on different params len 10
        self.graph.update(self.distribute(*self.energy_function())) 

        for i in range(self.size):
            if (self.graph.tiles[i].state is None):
                for j in range(10):
                    mean_creature_feedback[j]+=0
            else:
                decision_data = []
                lst = ([i]+list(self.graph.tiles[i].neightbours))
                out = []
                for el in lst:
                    out.append(self.graph.tiles[el].energy) #collecting own tile and neightbours energy
                decision_data.append(out)
                
                out = []
                for el in lst:
                    out.append(self.graph.tiles[el].state) #collecting own tile and neightbours info on creature presents and their stats
                decision_data.append(out)

                out = []
                for el in lst:
                    out.append(self.graph.tiles[el].tile_id) #collecting tile id, to move
                decision_data.append(out)
                #print(decision_data)

                lst_temp = self.graph.tiles[i].state.intellect(decision_data) #creature acts
                for j in range(10): 
                    mean_creature_feedback[j] += lst_temp[j]

                #moving
                for q in range(3):
                    if (self.get_neightbours(i)[q].state is None and self.get_neightbours(i)[q].tile_id == lst_temp[q]): #we can not override creature
                        self.graph.tiles[lst_temp[0]].state = self.graph.tiles[i].state
                        self.graph.tiles[i].state = None

                #taking energy
                old_energy = self.graph.tiles[i].energy
                self.graph.tiles[i].energy -= lst_temp[1]
                creature_penalty = 0 #might happen ifto much energy is taken, more then exists to compensate
                if (self.graph.tiles[i].energy < 0):
                    self.graph.tiles[i].energy = 0
                    creature_penalty = lst_temp[1] - old_energy #creature took to much energy #maybe remake to recentage based

                lst_temp[1]-=creature_penalty    

                #attack and paradite
                for q in range(3): #attack
                    if (self.get_neightbours(i)[q].state is not None): 
                        self.get_neightbours(i)[q].state.energy -= lst_temp[4]*2*1.0

                for q in range(3): #parasidte
                    if (self.get_neightbours(i)[q].state is not None):
                        self.get_neightbours(i)[q].state.energy -= lst_temp[4]*1.0

                #doing nothing
                """
                Nothing here ___
                """

                #mating
                for q in range(3):
                    if (self.get_neightbours(i)[q].state is None): #we can not override creature
                        if (random.random()*lst_temp[6] > 0.25 * lst_temp[6]): #if mating works out
                            self.get_neightbours(i)[q].state = Creature(self.get_neightbours(i)[q].tile_id,self)

                creature_gain = 0 

                lst_temp[1]+=creature_gain
                if (self.graph.tiles[i].state is not None): #creatues might have moved so better to double check
                    self.graph.tiles[i].state.update_biases(self.sreda.sreda_update_biases(lst_temp)) 

                    if (self.graph.tiles[i].state.is_alive == 0):
                        self.graph.tiles[i].energy += lst_temp[2] #energy creature releases
                        self.graph.tiles[i].state = None

        for el in mean_creature_feedback:
            el = el/self.size
        #sreda interaction based on creatures feedback
        self.sreda.interact_with_enviroment_global(mean_creature_feedback)
        self.save_file()
    
    def save_file(self):
        data = []
        for i in range(0, self.size, 1):
            #save structure = [tile_id/state, ]
            lst_temp = []

            #saving state 1/15
            x = self.graph.tiles[i].state
            if (x is None):
                x = 0
                lst_temp.append(x)
            else:
                x = 1
                lst_temp.append(x)

            #saving complexiry 2/15
            x = None
            if self.graph.tiles[i].state is None:
                lst_temp.append(0)
            else:
                x = self.graph.tiles[i].state.get_creature_complexity() 
                lst_temp.append(x)

            #saving aggresiveness 3/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (str(self.graph.tiles[i].state.dna)[1024:1152].count("1")/128)*9+1 #here I am mapping 128 0 to 0 10
                lst_temp.append(x)
            
            #saving sreda_noise 4/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x) #sibce no creature we assume 0
            else:
                x = (self.sreda.get_sreda_a() + self.sreda.get_sreda_b() + self.sreda.get_sreda_c())/3 + self.sreda.get_sreda_random_seed() 
                lst_temp.append(x)

            #saving Fertility 5/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (str(self.graph.tiles[i].state.dna)[1152:1280].count("1")/128)*9+1
                lst_temp.append(x)

            #saving Rigidness 6/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else: 
                x = (str(self.graph.tiles[i].state.dna)[384:512].count("1")/128)*9+1
                lst_temp.append(x)

            #saving Speed 7/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (str(self.graph.tiles[i].state.dna)[128:256].count("1")/128)*9+1
                lst_temp.append(x)

            #saving Energy cost 8/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = self.graph.tiles[i].state.calculate_energy_cost()
                lst_temp.append(x)

            #saving Energy storage 9/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (str(self.graph.tiles[i].state.dna)[640:768].count("1")/128)*9+1
                lst_temp.append(x)

            #saving Survivability 10/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (self.graph.tiles[i].state.memory_length ** 2)/10 #prolongued survival - quadtrtically better, for all creatures stars at t 1 and continues
                lst_temp.append(x)

            #saving Adaptability  11/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (self.graph.tiles[i].state.memory_length * self.sreda.adaptability) * self.sreda.get_sreda_random_seed() #at short distance slight noise to show that iniital adaptability is undecided 
                lst_temp.append(x)

            #saving Complexness storage 12/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = self.graph.tiles[i].state.get_creature_complexity()
                lst_temp.append(x)

            #saving Complexness dynamics 13/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = self.graph.tiles[i].state.get_creature_complexity() * (self.graph.tiles[i].state.memory_length * self.sreda.adaptability) * self.sreda.get_sreda_random_seed() #compolexity times adaptability, for complexity sum over time studies refer to the final thesis or report part 5
                lst_temp.append(x)
            
            #saving Impactfullness 14/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (self.sreda.get_sreda_a() + self.sreda.get_sreda_b() + self.sreda.get_sreda_c() + self.sreda.get_sreda_d() + self.sreda.get_sreda_e() + self.sreda.get_sreda_f())/6 + 3*self.sreda.get_sreda_random_seed() #Rudimentary, outdated, do not use 
                lst_temp.append(x)

            #saving Development 15/15
            x = 0
            if self.graph.tiles[i].state is None:
                lst_temp.append(x)
            else:
                x = (self.graph.tiles[i].state.get_creature_complexity() + (self.graph.tiles[i].state.memory_length * self.sreda.adaptability) + self.graph.tiles[i].state.get_creature_complexity() + self.graph.tiles[i].state.memory_length * 3 + self.graph.tiles[i].state.calculate_energy_cost() + (self.graph.tiles[i].state.memory_length ** 2) * 3 + (str(self.graph.tiles[i].state.dna)[1024:1152].count("1")/128)*9+1)**2/100 #surviability is weighted due to being very important, we divide by 100 to scale
                lst_temp.append(x)

            data.append(lst_temp)

        with open(f"temp_saves/save{self.trial_number}_{self.turn_number}.json", "w") as f: #we save with both trial and turn number, to avoid overwriting saves
            json.dump(data, f)

if __name__ == "__main__":
    """
    Space for test runs from this file. During real use I would be refering to graph.py from different files.
    """
    with open("faces.json", "r") as f:
        faces = json.load(f)

    graph = Graph()
    graph.build_graph(faces)
    #graph.debug_tiles()    

    e = Enviroment(graph,2)

    """
    lst2 = []

    for i in range(10000):
        e.turn_update()
        graph.update(e.distribute(*e.energy_function()))
        lst2.append(graph.tiles[0].energy)
    
    with open('empty_energy_capped_low.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for value in lst2:
            writer.writerow([value])   
    """
    #spawn creatures
    c = Creature(0,e)
    c1 = Creature(1,e)

    e.add_creature(c)
    e.add_creature(c1)

    for i in range(2500):
        e.next_turn()