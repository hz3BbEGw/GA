import sys
from tqdm import tqdm
from .models import ProblemInput, ProblemOutput, AssignmentResult, CriterionType, ProblemStats, RankingsStats, MinimizeCriterionStats
from .genetic.population import Population

def _compute_stats(data: ProblemInput, assignments):
    student_map = {s.id: s for s in data.students}
    group_students = {g.id: [] for g in data.groups}
    for assignment in assignments:
        group_students.setdefault(assignment.group_id, []).append(assignment.student_id)

    rankings_stats = None
    if any(s.rankings for s in data.students):
        rank_values = []
        for assignment in assignments:
            student = student_map.get(assignment.student_id)
            if not student or not student.rankings:
                continue
            rank_values.append(student.rankings.get(assignment.group_id, 0.0))
        if rank_values:
            rankings_stats = RankingsStats(
                avg_rank=sum(rank_values) / len(rank_values),
                min_rank=min(rank_values),
            )

    minimize_groups = {}
    for g in data.groups:
        for c_name, configs in g.criteria.items():
            if any(c.type == CriterionType.MINIMIZE for c in configs):
                minimize_groups.setdefault(c_name, []).append(g.id)

    minimize_stats = None
    if minimize_groups:
        minimize_stats = {}
        for c_name, group_ids in minimize_groups.items():
            if data.students:
                global_mean = sum(s.values.get(c_name, 0) for s in data.students) / len(data.students)
            else:
                global_mean = 0.0

            group_avgs = []
            for g_id in group_ids:
                student_ids = group_students.get(g_id, [])
                if not student_ids:
                    continue
                total = sum(student_map[s_id].values.get(c_name, 0) for s_id in student_ids)
                group_avgs.append(total / len(student_ids))

            if len(group_avgs) >= 2:
                max_group_avg_diff = max(group_avgs) - min(group_avgs)
            else:
                max_group_avg_diff = 0.0

            if group_avgs:
                max_group_global_diff = max(abs(avg - global_mean) for avg in group_avgs)
            else:
                max_group_global_diff = 0.0

            minimize_stats[c_name] = MinimizeCriterionStats(
                max_group_avg_diff=max_group_avg_diff,
                max_group_global_diff=max_group_global_diff,
            )

    has_prereq = False
    prerequisites_ok = True
    for g in data.groups:
        for c_name, configs in g.criteria.items():
            for c_config in configs:
                if c_config.type != CriterionType.PREREQUISITE or c_config.min_ratio is None:
                    continue
                has_prereq = True
                threshold = c_config.min_ratio
                for s_id in group_students.get(g.id, []):
                    if student_map[s_id].values.get(c_name, 0) < threshold:
                        prerequisites_ok = False
                        break
                if not prerequisites_ok:
                    break
            if not prerequisites_ok:
                break
        if not prerequisites_ok:
            break

    prerequisites_met = prerequisites_ok if has_prereq else None

    if not rankings_stats and not minimize_stats and prerequisites_met is None:
        return None

    return ProblemStats(
        rankings=rankings_stats,
        minimize=minimize_stats,
        prerequisites_met=prerequisites_met,
    )

def _run_single_ga(
    data: ProblemInput,
    show_progress: bool,
    run_index: int,
    total_runs: int,
):
    # GA parameters
    POPULATION_SIZE = 120
    GENERATIONS = 200
    CROSSOVER_RATE = 1
    MUTATION_RATE = 0.28
    ELITISM = 6

    # Initialize population
    population = Population(data, size=POPULATION_SIZE)
    
    # Track initial best fitness
    initial_best = population.get_best()
    initial_fitness = initial_best.fitness
    
    # Evolution loop
    run_label = f"GA {run_index + 1}/{total_runs}" if total_runs > 1 else "GA"
    progress = tqdm(range(GENERATIONS), desc=run_label, unit="gen", disable=not show_progress)
    for _ in progress:
        population.evolve(
            crossover_rate=CROSSOVER_RATE, 
            mutation_rate=MUTATION_RATE, 
            elitism=ELITISM
        )
        best = population.get_best()
        progress.set_postfix(best_fitness=f"{best.fitness:.2f}")
        
    # Get final best
    final_best = population.get_best()
    return final_best, initial_fitness

def solve_assignment(data: ProblemInput, show_progress: bool = False, runs: int = 5) -> ProblemOutput:
    runs = max(1, runs)
    best_overall = None
    best_initial_fitness = None
    best_run = 1

    for run_index in range(runs):
        final_best, initial_fitness = _run_single_ga(
            data=data,
            show_progress=show_progress,
            run_index=run_index,
            total_runs=runs,
        )
        if best_overall is None or final_best.fitness < best_overall.fitness:
            best_overall = final_best
            best_initial_fitness = initial_fitness
            best_run = run_index + 1
    
    # Format results
    assignments = [
        AssignmentResult(student_id=s_id, group_id=g_id)
        for s_id, g_id in best_overall.genes.items()
    ]
    assignments.sort(key=lambda a: a.student_id)
    
    status = f"FITNESS: {best_overall.fitness}; INITIAL FITNESS: {best_initial_fitness}; "

    return ProblemOutput(
        assignments=assignments,
        status=status,
        stats=_compute_stats(data, assignments),
    )
