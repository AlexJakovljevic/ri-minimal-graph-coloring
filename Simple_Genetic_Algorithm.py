import random, heapq, time, os
from operator import attrgetter


class Genetic_Algorithm:

    def __init__(self, n_colors):
        self._allowed_gene_values = [i for i in
                                     range(n_colors)]
        self._generation_size = 50
        self._mutation_rate = 0.7
        self._reproduction_size = 25
        self._current_iteration = 0
        self._top_chromosome = None
        self._tournament_k = 4
        self._num_vertices = 0
        self._target = 0
        self._adjacency_list = {}
        self._elite_size = 3
        self._num_of_colors = n_colors

    def optimize(self):
        chromosomes = self.initial_population()
        self._top_chromosome = Chromosome(min(chromosomes, key=attrgetter('fitness')),
                                          min(chromosomes, key=attrgetter('fitness')).fitness)
        while not self.stop_condition():
            new_generation = heapq.nlargest(self._elite_size, chromosomes)
            for_reproduction = self.selection_tournament(chromosomes)
            chromosomes = self.create_generation(for_reproduction, new_generation)
            self._top_chromosome = Chromosome(min(chromosomes, key=attrgetter('fitness')),
                                              min(chromosomes, key=attrgetter('fitness')).fitness)
            self._current_iteration += 1
        print(self._current_iteration)

        return self._top_chromosome, self._current_iteration

    def create_generation(self, for_reproduction, new_generation):
        new_gen_len = len(new_generation)
        while new_gen_len < self._generation_size:
            parents = random.sample(for_reproduction, 2)
            child1, child2 = self.one_point_crossover(parents[0].content, parents[1].content)
            child1 = self.mutation(child1)
            child2 = self.mutation(child2)

            new_generation.append(Chromosome(child1, self.fitness(child1)))
            new_generation.append(Chromosome(child2, self.fitness(child2)))
            new_gen_len += 2

        return new_generation

    def one_point_crossover(self, a, b):
        bp = random.randrange(1, self._num_vertices - 1)
        child1 = a[:bp] + b[bp:]
        child2 = b[:bp] + a[bp:]
        return child1, child2

    def two_point_crossover(self, a, b):
        bp = random.randrange(1, self._num_vertices - 1)
        bp2 = random.randrange(1, self._num_vertices - 1)
        child1 = a[:bp] + b[bp:bp2] + a[bp2:]
        child2 = b[:bp] + a[bp:bp2] + b[bp2:]
        return child1, child2

    def mutation(self, chromosome):
        t = random.random()
        if t < self._mutation_rate:
            i = random.randrange(0, self._num_vertices - 1)
            chromosome[i] = random.choice(self._allowed_gene_values)
        return chromosome

    def selection_tournament(self, chromosomes):
        return [self.selection_tournament_pick(chromosomes, self._tournament_k) for i in
                range(self._reproduction_size)]

    def selection_tournament_pick(self, chromosomes, k):
        picked = []
        best_i = None
        for i in range(k):
            pick = random.randint(0, self._generation_size - 1)
            picked.append(chromosomes[pick])
            if best_i is None or picked[i].fitness < picked[best_i].fitness:
                best_i = i
        return picked[best_i]

    def fitness(self, chromosome):
        fitness_value = 0
        for i in range(self._num_vertices):
            for j in self._adjacency_list[i]:
                if chromosome[i] == chromosome[j]:
                    fitness_value += 1
        return fitness_value

    def initial_population(self):
        init_pop = []
        for i in range(self._generation_size):
            genetic_code = []
            for k in range(self._num_vertices):
                genetic_code.append(random.choice(self._allowed_gene_values))
            init_pop.append(genetic_code)
        init_pop = [Chromosome(content, self.fitness(content)) for content in init_pop]
        return init_pop

    def stop_condition(self):
        return self._current_iteration > self._iterations or self._top_chromosome.fitness == self._target


class Chromosome:

    def __init__(self, content, fitness):
        self.content = content
        self.fitness = fitness

    def __str__(self): return "%s f=%d" % (self.content, self.fitness)

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __repr__(self): return "%s f=%d" % (self.content, self.fitness)


if __name__ == "__main__":

    graph_list = []
    rootDir = './graphs'
    for dirName, subdirList, fileList in os.walk(rootDir):
        print('Found directory: %s' % dirName)
        for fname in fileList:
            graph_list.append(fname)

    for graph_name in graph_list:
        test_vals = []
        test_iters = []
        success_rate = []
        minimal_chromatic_number = 0
        number_of_tests = 50
        while number_of_tests > 0:
            i = minimal_chromatic_number
            final_time = 0
            total_iters = 0
            while i > minimal_chromatic_number - 1:
                print("Loading data...")
                with open("graphs/" + str(graph_name), "r") as graph_file:
                    minimal_chromatic_number = int(graph_file.readline())
                    i = minimal_chromatic_number
                    genetic = Genetic_Algorithm(i)
                    first_line = graph_file.readline().split(" ")
                    genetic._num_vertices = int(first_line[0])
                    genetic._adjacency_list = {i: [] for i in range(genetic._num_vertices)}
                    genetic._target = 0
                    for line in graph_file:
                        edge = line.split(" ")
                        genetic._adjacency_list[int(edge[0]) - 1].append(int(edge[1]) - 1)

                print("Executing simple generic algorithm for " + graph_name + " " + str(
                    51 - number_of_tests) + ". time...")
                start = time.time()
                solution, iters = genetic.optimize()
                end = time.time()
                iter_time = end - start
                final_time += iter_time
                total_iters += iters
                print("Solution for %d in %f: %s fitness: %d" % (i, final_time, solution.content, solution.fitness))
                if solution.fitness == genetic._target:
                    i -= 1
                    test_vals.append(iter_time)
                    test_iters.append(iters)
                    final_time = 0
                    total_iters = 0
                    success_rate.append(1)
                else:
                    success_rate.append(0)

            number_of_tests -= 1
        with open("results/results_simple.txt", "a+") as results:
            results.write(graph_name + "\n")
            results.write(str(test_vals) + "\n")
            results.write(str(test_iters) + "\n")

        with open("analysis/success_rate_simple.txt", "a+") as success_file:
            success_file.write(graph_name + ":\n")
            success_file.write(str(success_rate))
            success_file.write("\n")

