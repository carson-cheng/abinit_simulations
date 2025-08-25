import os
import numpy as np
import time
from multiprocessing import Pool
strings = []

def run_one_iteration(args):
    iteration, item = args
    input_file = open("input_file.abi").read()
    lines = input_file.split("\n")
    current_line = None
    for i in lines:
        if "ratsph" in i:
            current_line = i
            break
    new_line = f"ratsph {str(item)}"
    printstring = ""
    printstring += f"{current_line}, {new_line}\n"
    input_file = input_file.replace(current_line, new_line)
    
    # Create a temporary input file for this process to avoid conflicts
    temp_input_file = f"input_file_{iteration}.abi"
    with open(temp_input_file, "w") as wf:
        wf.write(input_file)
    
    new_line = current_line
    printstring += "Running abinit...\n"
    output_fn = f"base_output_{iteration}.txt"
    status = os.system(f"abinit {temp_input_file} > {output_fn}")
    printstring += "Analyzing output file...\n"
    contents = open(f"{output_fn}").read()
    section = contents.split("Radius=ratsph(iatom)")[1].split("================")[0]
    sum_section = section.split("Sum")[1].split("\n")[0]
    numbers = [x for x in sum_section.split(" ") if "." in x]
    numbers = [float(x) for x in numbers]
    printstring += f"{numbers[2]}"
    
    # Clean up temporary input file
    os.remove(temp_input_file)
    
    return printstring

if __name__ == '__main__':
    start = time.time()
    sizes = np.linspace(1e-06, 5.0, 24)
    for i in range(8):
        strings = []
        # Create a list of arguments for each iteration
        size_subset = sizes[i*3:(i+1)*3]
        tasks = [(i, size_subset[i]) for i in range(len(size_subset))]
        
        # Use multiprocessing Pool to run iterations in parallel
        with Pool(processes=len(sizes)) as pool:
            results = pool.map(run_one_iteration, tasks)
        
        # Store and print results
        strings.extend(results)
        print(size_subset)
        print(strings)
    
    print(time.time() - start)