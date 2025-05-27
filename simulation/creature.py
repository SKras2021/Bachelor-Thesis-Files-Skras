import random
import string
from typing import List
import statistics

class Creature:
    def __init__(self, location, enviroment, parent_a_dna = None, parent_b_dna = None, sreda_mutation_chance = 0.0015, biases_length = 128):
        if (parent_a_dna is None):
            parent_a_dna = self.generate_random_creature() #we make inital generation and then merge it to prevent overflu chaotic creatures from appearing
        if (parent_b_dna is None):
            parent_b_dna = self.generate_random_creature()
        self.biases_length = biases_length
        self.location = location
        self.dna = self.mutate(self.reproduce_calc_result(parent_a_dna, parent_b_dna), sreda_mutation_chance)
        self.biases = "".join(random.choice("0123456789") for _ in range(biases_length)) #memory
        self.energy = self.dna[640:768].count("1") * 0.75
        self.memory_length = 1 #not biases length, how much updates creature's mind got
        self.enviroment = enviroment
        self.is_alive = 1

    def generate_random_creature(self) -> str:
        """
        |Physical characteristics|
        0 - 128 : size
        128 - 256 : speed
        256 - 384 : intellect
        384 - 512 : rigidness
        512 - 640 : strength
        640 - 768 : energy storage
        768 - 894 : attractiveness
        894 - 1024 : sreda block reserve
        |Behavioral biases|
        1024 - 1152 : agressiveness
        1152 - 1280 : propencity to mate
        1280 - 1408 : preference for predation
        1408 - 1536 : lazyness
        1536 - 1664 : propensity to store energy for later
        1664 - 1792 : inovativeness
        1792 - 1920 : propensity for a parasitic lifestyle
        1920 - 2048 : sreda block reserve
        """
        #genome length 2048, but it is subdivided in sections
        genome = "".join(random.choice("01") for _ in range(2048))

        return genome
    
    def reproduce_calc_result(self, a, b):
        """
        Due to the specificty of a genome structure recreating the merging system from the 
        progesss logs would be the potentially a possible implementatoin, due to the fact that it merges them without looking at the dedicated segments
        So I have decided to go element by element and avoid averaging instead. a and b are obviously supposed to be eual to each other
        """
        new_genome = ""

        for i in range(len(a)): 
            if (random.random() < 0.5):
                new_genome += a[i] 
            else:
                new_genome += b[i] 
        
        return new_genome

    def mutate(self, genome, mutation_chance, segment_length = 128):
        """
        We traverse the string charavter by character, each time with mutation_chance the character is "inverted" (type a mutation)
        Due to the segmented structure the ending parts are more likely to evolve, because otherwise the mutations would be way to drastic.
        """
        new_genome = ""
        counter = 0
        for el in genome:
            counter+=1
            mutation_chance_weighted = mutation_chance #* (((counter % segment_length)+1)/segment_length) #closer to ending higher probabulity to mutate, but never 0 cause of +1
            if (random.random() < mutation_chance_weighted):
                new_genome+=random.choice(string.ascii_lowercase) 
            else:
                new_genome+=el 

        return new_genome

    def intellect(self, decision_data):
        #here a creature decidedes on it's action some are determined by dna, some by in-life developed biases.
        #first we need to look at the neightbours
        #we are getting decision data with info on neightboring creatures and energy distribution
        """
        Decision data [[a,b,c,d], [e,f,g,h], [x,y,v,w]]
        a = own tile energy
        b = neightbour tile 1 energy
        c = neightbour tile 2 energy
        d = neightbour tile 3 energy

        e = info on oneself (rudiment for better shape orginally used)
        f = neightbour 1 info None = no neightbour
        g = neightbour 2 info None = no neightbour
        h = neightbour 3 info None = no neightbour
        """
        enviromental_effect = [0]*10

        data = self.look_around()

        creatues_around = 0

        for el in data:
            if (el != None):
                creatues_around += 1

        #print(f"There is/are {creatues_around} creature(s) next to us")

        
        """
        A creature needs to choose an action now. It can attack neightboring creature if any, breed neghboring creature if any, parasite neightbour if any
        It can also spend energy to move. Each action has energy cost multipliar, just by exiswting creature consumes energy by taking an action more is consumed, creature can 
        As well do nothing, athough it is a losing strategy. Better would be to collect some energy from the enviroment
        """
        ratio_allocations = [0,0,0,0,0,0] #element 0 - attack, 1 - breed, 2 - parasite, 3 - move, 4 - do nothing factor, 5 take from enviroment

        ratio_allocations[0] = 1 + self.dna[1024:1152].count("1") + int(self.biases[0]) + sum(decision_data[0])
        ratio_allocations[1] = 1 + (self.dna[1152:1280].count("1") + self.dna[768:894].count("1"))/2 + int(self.biases[1]) + sum(decision_data[0])
        ratio_allocations[2] = 1 + self.dna[1792:1920].count("1") + int(self.biases[2]) + sum(decision_data[0])
        ratio_allocations[3] = 1 + self.dna[128:256].count("1") + int(self.biases[3]) + sum(decision_data[2])
        ratio_allocations[4] = 1 + self.dna[1408:1536].count("1") + int(self.biases[4]) + int(sum(decision_data[0]) * 0.01)

        y = self.dna[640:768].count("1") - self.energy + int(self.biases[5]) + sum(decision_data[0])

        if (y < 0):
            y = 0
        ratio_allocations[5] = y*5 #can not go beyond maximum energy capacity, multiplied to factor of the energy subrtaction

        if (creatues_around == 0): #should be negative, since when creature would have noone to breed with it would be biased against of doing this, but since an error will be caused even by 0.0001 value we are manually aetting them to zero to avoid it, and that positive values appearing not due to biases, but diu to genetic predisposition
            ratio_allocations[0] = 0
            ratio_allocations[1] = 0
            ratio_allocations[2] = 0
    
        total = sum(ratio_allocations)
        ratio_allocations_normalised = [el/total for el in ratio_allocations] #must be sum = 1 assert

        delta = self.calculate_energy_cost()
        #print(ratio_allocations_normalised, self.energy, delta)

        energy_allocation = [el * delta for el in ratio_allocations_normalised] #adds up to delta assert
        

        if (energy_allocation[0] > energy_allocation[1]):
            #either mate or fight, there might be simulations where both happen, but they are quite imporbable so we explude them for our intends and purposes
            energy_allocation[0] = energy_allocation[0] + energy_allocation[1]
            energy_allocation[1] = 0 

        if (energy_allocation[1] > energy_allocation[0]):
            #either mate or fight, there might be simulations where both happen, but they are quite imporbable so we explude them for our intends and purposes
            energy_allocation[1] = energy_allocation[0] + energy_allocation[1]
            energy_allocation[0] = 0 

        anti_alive = 0
        if (self.is_alive == 1):
            anti_alive = 0
        else:
            anti_alive = 1

        #print(energy_allocation)
        #Now that actions are chosen and energy is allocated to it it is time to execute them

        #fight. You neightbours lose 2x energy, but you gain nothing.
        #breed. 
        enviromental_effect[0] = int(energy_allocation[3])
        enviromental_effect[1] = int(energy_allocation[5])*5
        enviromental_effect[2] = anti_alive * int(self.calculate_energy_cost() * 5) #when dead release energy into the world of former power
        enviromental_effect[3] = int(energy_allocation[0])
        enviromental_effect[4] = int(energy_allocation[2]*2)
        enviromental_effect[5] = 6 - int(energy_allocation[4]*6)
        enviromental_effect[6] = int(energy_allocation[1] * 100)
        enviromental_effect[7] = int(((enviromental_effect[0] + enviromental_effect[1])/(enviromental_effect[3]+enviromental_effect[0] + enviromental_effect[1]))*10)
        enviromental_effect[8] = 1 - enviromental_effect[7] + enviromental_effect[2]
        enviromental_effect[9] = 1 - enviromental_effect[7] + enviromental_effect[2] + enviromental_effect[0]

        #handle energy
        self.energy -= delta
        self.energy += enviromental_effect[1]
        if (self.energy < 0):
            self.is_alive = 0

        #Creature feedback 
        """
        enviromental_effect[0] id to which creature moved (can stay the same)
        enviromental_effect[1] energy creature took from enviroment
        enviromental_effect[2] energy creature deposited to the enviroment
        enviromental_effect[3] energy taken from other creatures
        enviromental_effect[4] damage dealt to other creatures
        enviromental_effect[5] overall number of actions taken
        enviromental_effect[6] breeding chance
        enviromental_effect[7] ratio of agressive actioms
        enviromental_effect[8] ratio of peacefull actions energy consumption
        enviromental_effect[9] ratio of peacefull actions energy consumption #all /10 int(s) 0-9 inclusive
        """
        return enviromental_effect

    def look_around(self):
        lst = []

        x = self.enviroment.get_neightbours(self.location)

        for el in x:
            lst.append(el.state)

        return lst
    
    def update_biases(self, sreda_feedback: List) -> None:
        self.memory_length += 1
        #just update, do not return anything, even speicied
        sreda_biases = ""
        for i in range(len(sreda_feedback)):
            sreda_biases += sreda_feedback[i]
        
        self.biases = sreda_biases

    def calculate_energy_cost(self, segment_length = 128):
        """
        2 ** 128 per segment is way to much, let us just summ 1s, this would also make mutations simpler
        segments = [self.dna[i:i+segment_length] for i in range(0, len(self.dna), segment_length)]
        decimal_values = [int(segment, 2) for segment in segments]
        return decimal_values
        """
        segments = [self.dna[i:i+segment_length] for i in range(0, len(self.dna), segment_length)]
        decimal_values = [s.count("1") for s in segments]

        final_values = []

        for el in decimal_values:
            final_values.append(round(((el*0.21)**2) / 32, 3))

        return sum(final_values)/len(final_values) + (self.memory_length/10)**2 #memory length part is to simulate aging, the older the creature is the more energy it cosumes in the long run, short run opposite since young creatures need energy to grow, simulated by quadratic function

    def get_creature_complexity(self, segment_length = 12):
        segments = [self.dna[i:i+segment_length] for i in range(0, len(self.dna), segment_length)]
        decimal_values = [s.count("1") for s in segments]

        dna_complexity = sum(decimal_values) * 0.01
        biases = []
        for el in self.biases:
            biases.append(int(el))

        intelect_complexity = 0.25 * self.memory_length + 0.25 * dna_complexity + (sum(biases)/self.biases_length) * 0.25 + (statistics.stdev(biases) + statistics.stdev(decimal_values)) * 0.25

        return 0.10 * dna_complexity + 0.1 * self.memory_length + 0.8 * intelect_complexity
    
    def __str__(self):
        #Not repr, since repr must be unambigous, and I do not want to write out entire genome.
        return f"Creature located : {self.location} with energy {self.energy}"
    
#c = Creature(0)    
#print(c.calculate_energy_cost())