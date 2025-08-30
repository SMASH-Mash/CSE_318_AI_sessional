import random
import os
import csv

def graph_maker(graph_no):
    with open(graph_no, 'r') as f:
        lines = f.readlines()

    n, m = map(int, lines[0].split())
    adj_list = [[] for ii in range(n)]

    for line in lines[1:]:
        u, v, wght = map(int, line.split())
        u -= 1
        v -= 1
        adj_list[u].append((v, wght))
        adj_list[v].append((u, wght))  

    return n, m, adj_list



def randomized_max_cut(adj_list, iteration=100):
    num_vertices = len(adj_list)
    tot_weight = 0

    for ii in range(iteration):
        X = set()
        Y = set()

        for v in range(num_vertices):
            if random.random() >= 0.5:
                X.add(v)
            else:
                Y.add(v)

        cut_weight = 0
        visited = set()
        for u in range(num_vertices):
            for v, wght in adj_list[u]:
                if (u, v) not in visited and (v, u) not in visited:
                    if (u in X) != (v in X):
                        cut_weight += wght
                    visited.add((u, v))

        tot_weight += cut_weight

    return tot_weight / iteration


def greedy_max_cut(adj_list):
    n = len(adj_list)
    X, Y = set(), set()
    max_weight = -1
    max_wght_edge = (0, 1)

    for u in range(n):
        for v, wght in adj_list[u]:
            if u < v and wght > max_weight:
                max_weight = wght
                max_wght_edge = (u, v)

    u, v = max_wght_edge
    X.add(u)
    Y.add(v)
    U = set(range(n)) - {u, v}

    for z in U:
        wghtX = sum(wght for adjacent, wght in adj_list[z] if adjacent in Y)
        wghtY = sum(wght for adjacent, wght in adj_list[z] if adjacent in X)
        if wghtX > wghtY:
            X.add(z)
        else:
            Y.add(z)

    return X, Y


def semi_greedy(adj_list, alpha=0.3):
    n = len(adj_list)
    V = set(range(n))
    X, Y = set(), set()
    V_prime = V.copy()

    while V_prime:
        sigma_X = {v: sum(wght for u, wght in adj_list[v] if u in X) for v in V_prime}
        sigma_Y = {v: sum(wght for u, wght in adj_list[v] if u in Y) for v in V_prime}
        greedy_values = {v: max(sigma_X[v], sigma_Y[v]) for v in V_prime}

        wmin = min(min(sigma_X.values(), default=0), min(sigma_Y.values(), default=0))
        wmax = max(max(sigma_X.values(), default=0), max(sigma_Y.values(), default=0))

        mu = wmin + alpha * (wmax - wmin)

        RCL = [v for v in V_prime if greedy_values[v] >= mu]
        v_choice = random.choice(RCL) if RCL else random.choice(list(V_prime))

        if sigma_X[v_choice] >= sigma_Y[v_choice]:
            Y.add(v_choice)
        else:
            X.add(v_choice)

        V_prime.remove(v_choice)

    return X

def local_search(adj_list, Selected_set):
    n = len(adj_list)
    improved = True
    while improved:
        improved = False
        for v in range(n):
            gain = 0
            for u, wght in adj_list[v]:
                if (u in Selected_set) == (v in Selected_set):
                    gain += wght
                else:
                    gain -= wght
            if gain > 0:
                if (v in Selected_set):
                    Selected_set.remove(v)
                else:
                    Selected_set.add(v)
                improved = True
    return Selected_set

def cut_value_local(adj_list, Selected_set):
    total = 0
    for u in range(len(adj_list)):
        for v, wght in adj_list[u]:
            if u < v and ((u in Selected_set) != (v in Selected_set)):
                total += wght
    return total

def GRASP_max_cut(adj_list, max_iterations=100, alpha=0.3):
    best_val = float('-inf')

    for ii in range(max_iterations):
        Selected_set = semi_greedy(adj_list, alpha)
        Selected_set = local_search(adj_list, Selected_set)
        val = cut_value_local(adj_list, Selected_set)
        if val > best_val:
            best_val = val

    return  best_val


def cut_value_greedy(adj_list, X, Y):
    total = 0
    for u in X:
        for v, wght in adj_list[u]:
            if v in Y:
                total += wght
    return total


best_known = [12078, 12084, 12077, 0, 0, 0, 0, 0, 0, 0, 
627, 621, 645, 3187, 3169, 3172, 0, 0, 0, 0, 0, 
14123, 14129, 14131, 0, 0, 0, 0, 0, 0, 0, 
1560, 1537, 1541, 8000, 7996, 8009, 0, 0, 0, 0, 0, 
7027, 7022, 7020, 0, 0, 6000, 6000, 5988, 0, 0, 0, 0]
def process_all_rud_files(folder_path, output_csv_path):

    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
    
        writer.writerow([
            "Problem", "", "", 
            "Constructive algorithm", "", "", 
            "Local search", "", 
            "GRASP", "", 
            "Known best solution or upper bound"
        ])
        print("First row written.")    
        
        writer.writerow([
            "Name", "|V| or n", "|E| or m", 
            "Simple Randomized or Randomized-1", 
            "Simple Greedy or Greedy-1", 
            "Semi-greedy-1", 
            "Simple local or local-1", "", 
            "GRASP-1", "", 
            ""
        ])
        print("Second row written.")
        
        writer.writerow([
            "", "", "", "", "", "", 
            "No. of iterations", "Average value", 
            "No. of iterations", "Best value", 
            ""
        ])
        print("Third row written.")
        for i in range(1, 55):
            file_name = f"g{i}.rud"
            graph_no = os.path.join(folder_path, file_name)
            n, m, adj_matrix = graph_maker(graph_no)


            graph_name = f"G{i}"
            rand1 = randomized_max_cut(adj_matrix, 50)
            X, Y = greedy_max_cut(adj_matrix)
            greedy1 = cut_value_greedy(adj_matrix, X, Y)
            semi_greedy1 = cut_value_local(adj_matrix, semi_greedy(adj_matrix))

            local_avg = 0
            for j in range(1, 6):
                local_sol = local_search(adj_matrix, semi_greedy(adj_matrix, 0.3))
                local_avg = local_avg+cut_value_local(adj_matrix, local_sol)
            local_avg = local_avg / 5
            grasp_best = GRASP_max_cut(adj_matrix, 50)


            writer.writerow([
                graph_name, n, m,
                rand1,
                greedy1,
                semi_greedy1,
                5, local_avg,
                50, grasp_best,
                best_known[i-1]
            ])
            print(f"row {i} written for {file_name}")


if __name__ == "__main__":
    folder_path = "./graphs"  
    output_csv_path = "Observed_data.csv"
    process_all_rud_files(folder_path, output_csv_path)
