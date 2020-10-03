import random

POPULATION = 100


class Individual(object):
	def __init__(self, chromosome):
		self.chromosome = chromosome
		# self.fitness = self.call_fitness()
		
		# ~~~~~~~~~~~~~~~~~~~~~~~~~~~fitness function


def call_fitness(board):
	fitness = 0
	
	for i in range(0, 8):
		q1 = board[i]
		for j in range(i + 1, 8):
			q2 = board[j]
			
			if q1 == q2:  # in same row
				fitness += 1
			elif j - i == q2 - q1:  # conflict
				fitness += 1
			elif j - 1 == q1 - q2:  # conflict
				fitness += 1
			
			# 28 is the most conflict!!!
	return 1 - (fitness / 28)
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~create chromosome


def create_chrom():
	return [(random.random() * 10) % 8 for _ in range(8)]
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~selection
	
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CROSSOVER


def crossover(population, size):
	if size % 2 != 0:
		print("ERROR")
	
	result = [len("") for i in range(size // 2)]
	pop_index = 0
	for i in range(0, size, 2):
		xover = [0, 0, 0, 0, 0, 0, 0, 0]
		xover_pnt = (random.random() * 10) % 8
		
		for j in range(0, 8):
			if j <= xover_pnt:
				print(i)
				val = population[i]
			else:
				val = population[i + 1]
			
			xover[j] = val
		
		result[pop_index] = xover
	
	return result


def selection(population):
	# comulative_f = [len("") for i in range(POPULATION)]
	comulative_f = [0] * POPULATION
	normal_f = 0.0
	comulative = 0
	total = 0
	
	for i in range(len(population)):
		total += call_fitness(population[i])
	
	for i in range(len(population)):
		normal_f = call_fitness(population[i]) / total
		comulative += normal_f
		comulative_f[i] = comulative
	
	# selected = [len("") for i in range(POPULATION)]
	selected = [0] * POPULATION
	
	max_rand = random.random() + 1
	for i in range(len(population)):
		rand = random.random() / max_rand
		ptr = 0
		
		while ptr < len(population) - 1:
			if comulative_f[ptr] >= rand:
				break
			
			ptr += 1
		
		selected[i] = population[ptr]
	
	return selected


def concat(p1, s1, p2, s2):
	return p1[:s1] + p2[:s2]


def main():
	# global POPULATION
	generation = 1
	
	population = [create_chrom() for _ in range(POPULATION)]
	print(population)
	
	while True:
		selected = selection(population)
		print(len(selected))
		new_pop = create_chrom()
		overal_conc = concat(selected, POPULATION, new_pop, POPULATION)
		print(len(overal_conc), len(new_pop))
		XOVER = crossover(population.copy(), 2 * POPULATION)
		population = XOVER
		
		best_f = call_fitness(population[0])
		best_index = 0
		
		for i in range(1, POPULATION):
			f = call_fitness(population[i])
			if f > best_f:
				best_f = f
				best_index = i
		
		if best_f == 1:
			print(population[best_index])
			print(generation)
			break
		
		generation += 1


if __name__ == '__main__':
	main()
