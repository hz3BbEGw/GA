import sys
from tqdm import tqdm
from .models import ProblemInput, ProblemOutput, AssignmentResult
from .genetic.population import Population

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
        status=status
    )
