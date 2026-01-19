from typing import Dict, List
from .chromosome import Chromosome
from ..models import ProblemInput, CriterionType

SCALING_FACTOR = 10000
HARD_CONSTRAINT_PENALTY = 1e12  # Very high penalty for hard constraints

def evaluate_fitness(chromosome: Chromosome, problem: ProblemInput) -> float:
    total_penalty = 0.0
    student_map = {s.id: s for s in problem.students}

    # Global mean per criterion (used for MINIMIZE targets).
    criterion_names = set()
    for g in problem.groups:
        criterion_names.update(g.criteria.keys())

    if problem.students:
        global_means = {
            c_name: sum(student_map[s.id].values.get(c_name, 0) for s in problem.students) / len(problem.students)
            for c_name in criterion_names
        }
    else:
        global_means = {c_name: 0.0 for c_name in criterion_names}
    
    # 1. Group size constraints
    group_counts = {g.id: 0 for g in problem.groups}
    for g_id in chromosome.genes.values():
        if g_id in group_counts:
            group_counts[g_id] += 1
            
    for g in problem.groups:
        diff = abs(group_counts[g.id] - g.size)
        if diff > 0:
            total_penalty += diff * HARD_CONSTRAINT_PENALTY

    # 2. Exclusion constraints
    # Group students by group_id
    groups_students: Dict[int, List[int]] = {g.id: [] for g in problem.groups}
    for s_id, g_id in chromosome.genes.items():
        if g_id in groups_students:
            groups_students[g_id].append(s_id)
            
    for pair in problem.exclude:
        if len(pair) >= 2:
            s1, s2 = pair[0], pair[1]
            g1 = chromosome.genes.get(s1)
            g2 = chromosome.genes.get(s2)
            if g1 is not None and g1 == g2:
                total_penalty += HARD_CONSTRAINT_PENALTY

    # 3. Criteria constraints and objectives
    for g in problem.groups:
        student_ids = groups_students[g.id]
        if not student_ids:
            # If group is empty but size > 0, size penalty already applied
            continue
            
        for c_name, configs in g.criteria.items():
            # Calculate group sum for this criterion
            # Scaled to match cpsat logic: sum(scaled_val * x)
            # scaled_val = int(s.values.get(c_name, 0) * SCALING_FACTOR)
            group_sum = sum(int(student_map[s_id].values.get(c_name, 0) * SCALING_FACTOR) for s_id in student_ids)
            
            for c_config in configs:
                if c_config.type == CriterionType.MINIMIZE:
                    target_sum = int(global_means.get(c_name, 0) * g.size * SCALING_FACTOR)
                    penalty = abs(group_sum - target_sum)
                    total_penalty += penalty

                elif c_config.type == CriterionType.PULL:
                    max_val = 0
                    for s_id in student_ids:
                        max_val = max(max_val, int(student_map[s_id].values.get(c_name, 0) * SCALING_FACTOR))
                    max_sum = max_val * g.size
                    penalty = max_sum - group_sum
                    total_penalty += penalty

                elif c_config.type == CriterionType.PREREQUISITE:
                    if c_config.min_ratio is not None:
                        threshold = int(c_config.min_ratio * SCALING_FACTOR)
                        # all students in group must be >= threshold
                        for s_id in student_ids:
                            val = int(student_map[s_id].values.get(c_name, 0) * SCALING_FACTOR)
                            if val < threshold:
                                total_penalty += HARD_CONSTRAINT_PENALTY
                                break

    # 4. Rankings objective (maximize total ranking, normalized to avoid dominance)
    if any(s.rankings for s in problem.students):
        ranking_scale = max(1, SCALING_FACTOR // max(1, len(criterion_names)))
        ranking_sum = 0
        for s_id, g_id in chromosome.genes.items():
            rankings = student_map[s_id].rankings
            if not rankings:
                continue
            rank_val = rankings.get(g_id, 0.0)
            ranking_sum += int(rank_val * ranking_scale)
        ranking_penalty = ranking_scale * len(problem.students) - ranking_sum
        total_penalty += ranking_penalty
                                
    chromosome.fitness = total_penalty
    return total_penalty
