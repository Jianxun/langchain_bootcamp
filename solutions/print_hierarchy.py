#!/usr/bin/env python3

import json
from pathlib import Path
from collections import defaultdict

def should_skip_solution(title: str) -> bool:
    """
    Check if a solution should be skipped based on its title.
    
    Args:
        title (str): Solution title to check
        
    Returns:
        bool: True if solution should be skipped, False otherwise
    """
    skip_phrases = [
        "Applicable Technology Solutions",
        "Industry Applications",
        "A<sup>2</sup>B Audio Bus"
    ]
    return any(phrase in title for phrase in skip_phrases)

def filter_solutions(solutions):
    """
    Filter out unwanted solutions and their sub-solutions.
    
    Args:
        solutions (list): List of solution dictionaries
        
    Returns:
        list: Filtered list of solutions
    """
    filtered = []
    for solution in solutions:
        if should_skip_solution(solution['title']):
            continue
            
        if 'sub_solutions' in solution:
            solution['sub_solutions'] = filter_solutions(solution['sub_solutions'])
            if not solution['sub_solutions']:  # If no sub-solutions left
                del solution['sub_solutions']
                
        filtered.append(solution)
    return filtered

def find_duplicates(solution, title_to_paths, current_path):
    """
    Find duplicate solutions and their paths in the hierarchy.
    
    Args:
        solution (dict): Solution dictionary
        title_to_paths (dict): Dictionary mapping titles to their paths
        current_path (list): Current path in the hierarchy
    """
    title = solution['title']
    current_path.append(title)
    
    # Store the path for this title
    title_to_paths[title].append(' > '.join(current_path))
    
    # Recursively check sub-solutions
    if 'sub_solutions' in solution:
        for sub_solution in solution['sub_solutions']:
            find_duplicates(sub_solution, title_to_paths, current_path)
    
    current_path.pop()

def print_solution_tree(solution, prefix="", is_last=True, output_lines=None):
    """
    Print a solution and its sub-solutions in a tree-like structure.
    
    Args:
        solution (dict): Solution dictionary
        prefix (str): Prefix for indentation
        is_last (bool): Whether this is the last item at this level
        output_lines (list): List to store output lines if provided
    """
    # Prepare the line
    connector = "└── " if is_last else "├── "
    line = f"{prefix}{connector}{solution['title']}"
    
    # Print to console
    print(line)
    
    # Store in output_lines if provided
    if output_lines is not None:
        output_lines.append(line)
    
    # Print sub-solutions if they exist
    if 'sub_solutions' in solution:
        # Update prefix for next level
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Print each sub-solution
        for i, sub_solution in enumerate(solution['sub_solutions']):
            is_last_sub = (i == len(solution['sub_solutions']) - 1)
            print_solution_tree(sub_solution, new_prefix, is_last_sub, output_lines)

def create_title_hierarchy(solution):
    """
    Create a simplified hierarchy as a nested object structure.
    
    Args:
        solution (dict): Solution dictionary
        
    Returns:
        dict: Simplified hierarchy as a nested object
    """
    result = {}
    
    if 'sub_solutions' in solution and solution['sub_solutions']:
        # Create a nested object for each sub-solution
        for sub_solution in solution['sub_solutions']:
            result.update(create_title_hierarchy(sub_solution))
    
    return {solution['title']: result}

def main():
    # Read the JSON file
    script_dir = Path(__file__).parent
    json_file = script_dir / "parsed_solutions.json"
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            solutions = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found. Please run parse_solutions.py first.")
        return
    except json.JSONDecodeError:
        print(f"Error: {json_file} is not valid JSON.")
        return
    
    # Filter solutions
    filtered_solutions = filter_solutions(solutions)
    
    # Prepare the output text
    output_lines = []
    output_lines.append("\nAnalog Devices Solutions Hierarchy (Filtered):")
    output_lines.append("=" * 50)
    
    for i, solution in enumerate(filtered_solutions):
        is_last = (i == len(filtered_solutions) - 1)
        # Capture the output in a list
        solution_lines = []
        print_solution_tree(solution, "", is_last, solution_lines)
        output_lines.extend(solution_lines)
    
    # Save filtered solutions to a new JSON file
    output_json = script_dir / "filtered_solutions.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(filtered_solutions, f, indent=2, ensure_ascii=False)
    print(f"\nFiltered solutions saved to {output_json}")
    
    # Save hierarchy to a text file
    output_txt = script_dir / "solutions_hierarchy.txt"
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    print(f"Hierarchy saved to {output_txt}")
    
    # Create and save simplified title-only hierarchy
    title_hierarchy = {}
    for solution in filtered_solutions:
        title_hierarchy.update(create_title_hierarchy(solution))
    title_json = script_dir / "solutions_hierarchy.json"
    with open(title_json, 'w', encoding='utf-8') as f:
        json.dump(title_hierarchy, f, indent=2, ensure_ascii=False)
    print(f"Title hierarchy saved to {title_json}")

if __name__ == "__main__":
    main() 