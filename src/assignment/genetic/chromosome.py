import random
from typing import Dict, List
from ..models import ProblemInput

class Chromosome:
    def __init__(self, genes: Dict[int, int]):
        self.genes = genes
        self.fitness: float = float('inf')

    @classmethod
    def random_initialization(cls, problem: ProblemInput) -> 'Chromosome':
        """Create a size-balanced random assignment respecting possible_groups."""
        genes = {}
        
        group_sizes = {g.id: g.size for g in problem.groups}
        remaining = group_sizes.copy()

        student_map = {s.id: s for s in problem.students}
        student_ids = [s.id for s in problem.students]
        random.shuffle(student_ids)
        student_ids.sort(key=lambda s_id: len(student_map[s_id].possible_groups))

        fallback_group = problem.groups[0].id if problem.groups else 0

        for s_id in student_ids:
            student = student_map[s_id]
            if not student.possible_groups:
                genes[s_id] = fallback_group
                continue

            feasible = [g_id for g_id in student.possible_groups if remaining.get(g_id, 0) > 0]
            if feasible:
                # Prefer groups with more remaining capacity, tie-break randomly
                max_remaining = max(remaining[g_id] for g_id in feasible)
                best = [g_id for g_id in feasible if remaining[g_id] == max_remaining]
                chosen = random.choice(best)
            else:
                chosen = random.choice(student.possible_groups)

            genes[s_id] = chosen
            if chosen in remaining:
                remaining[chosen] -= 1
                
        return cls(genes)

    def copy(self) -> 'Chromosome':
        return Chromosome(self.genes.copy())
