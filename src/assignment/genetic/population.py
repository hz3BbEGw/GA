from typing import List
from .chromosome import Chromosome
from .fitness import evaluate_fitness
from .operators import tournament_selection, uniform_crossover, swap_mutation, random_mutation
from ..models import ProblemInput

class Population:
    def __init__(self, problem: ProblemInput, size: int = 100):
        self.problem = problem
        self.size = size
        self.individuals: List[Chromosome] = [
            Chromosome.random_initialization(problem) for _ in range(size)
        ]
        self.evaluate()

    def evaluate(self):
        for individual in self.individuals:
            evaluate_fitness(individual, self.problem)

    def evolve(self, crossover_rate: float = 0.8, mutation_rate: float = 0.2, elitism: int = 2):
        new_population: List[Chromosome] = []
        
        # Elitism
        self.individuals.sort(key=lambda x: x.fitness)
        new_population.extend([ind.copy() for ind in self.individuals[:elitism]])
        
        import random
        while len(new_population) < self.size:
            # Selection
            parent1 = tournament_selection(self.individuals)
            parent2 = tournament_selection(self.individuals)
            
            # Crossover
            if random.random() < crossover_rate:
                child = uniform_crossover(parent1, parent2)
            else:
                child = parent1.copy()
            
            # Mutation
            # Use swap mutation as requested, and a bit of random mutation to escape local optima
            child = swap_mutation(child, self.problem, mutation_rate)
            # child = random_mutation(child, self.problem, mutation_rate * 0.5)
            
            new_population.append(child)
            
        self.individuals = new_population
        self.evaluate()

    def get_best(self) -> Chromosome:
        return min(self.individuals, key=lambda x: x.fitness)
