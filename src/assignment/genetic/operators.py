import random
from typing import List
from .chromosome import Chromosome
from ..models import ProblemInput

def tournament_selection(population: List[Chromosome], k: int = 3) -> Chromosome:
    """Select the best individual from a random sample of k individuals."""
    selection = random.sample(population, k)
    return min(selection, key=lambda x: x.fitness)

def uniform_crossover(parent1: Chromosome, parent2: Chromosome) -> Chromosome:
    """Create a child by randomly choosing genes from each parent."""
    child_genes = {}
    for s_id in parent1.genes.keys():
        if random.random() < 0.5:
            child_genes[s_id] = parent1.genes[s_id]
        else:
            child_genes[s_id] = parent2.genes[s_id]
    return Chromosome(child_genes)

def swap_mutation(chromosome: Chromosome, problem: ProblemInput, mutation_rate: float = 0.2) -> Chromosome:
    """Mutate by swapping group assignments between two students."""
    if random.random() > mutation_rate:
        return chromosome

    new_genes = chromosome.genes.copy()
    student_ids = list(new_genes.keys())
    
    if len(student_ids) < 2:
        return chromosome

    s1_id, s2_id = random.sample(student_ids, 2)
    g1_id = new_genes[s1_id]
    g2_id = new_genes[s2_id]

    if g1_id == g2_id:
        return chromosome

    student_map = {s.id: s for s in problem.students}
    s1_possible = student_map[s1_id].possible_groups
    s2_possible = student_map[s2_id].possible_groups

    if g2_id in s1_possible and g1_id in s2_possible:
        new_genes[s1_id] = g2_id
        new_genes[s2_id] = g1_id

    return Chromosome(new_genes)

def random_mutation(chromosome: Chromosome, problem: ProblemInput, mutation_rate: float = 0.1) -> Chromosome:
    """Change one student's group assignment."""
    if random.random() > mutation_rate:
        return chromosome

    new_genes = chromosome.genes.copy()
    s_id = random.choice(list(new_genes.keys()))
    
    student_map = {s.id: s for s in problem.students}
    possible = student_map[s_id].possible_groups
    if possible:
        new_genes[s_id] = random.choice(possible)
        
    return Chromosome(new_genes)
