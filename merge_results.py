#!/usr/bin/env python3
"""
Merge game logic results with existing experiment_results_full file.
Adds game_logic_passed field to existing results.
"""

import json
import os
import glob

def load_json_file(filename):
    """Load JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def merge_game_logic_results(full_results_file, logic_results_file, output_file):
    """Merge game logic results into full results"""
    
    # Load both files
    full_results = load_json_file(full_results_file)
    logic_results = load_json_file(logic_results_file)
    
    if full_results is None or logic_results is None:
        print("Failed to load results files")
        return False
    
    print("="*70)
    print("MERGING GAME LOGIC RESULTS")
    print("="*70)
    print(f"Full results: {full_results_file}")
    print(f"Logic results: {logic_results_file}")
    print(f"Output: {output_file}")
    print("="*70)
    print()
    
    # Merge game logic data into full results
    merged_count = 0
    total_count = 0
    
    for game_name in full_results.keys():
        if game_name not in logic_results:
            print(f"  Warning: {game_name} not found in logic results")
            continue
        
        if 'gemini' not in full_results[game_name]:
            continue
        
        if 'gemini' not in logic_results[game_name]:
            continue
        
        full_list = full_results[game_name]['gemini']
        logic_list = logic_results[game_name]['gemini']
        
        # Match by index (assuming same order)
        min_len = min(len(full_list), len(logic_list))
        
        for i in range(min_len):
            total_count += 1
            if 'game_logic_passed' in full_list[i]:
                continue  # Already merged
            
            # Add game logic fields
            full_list[i]['game_logic_passed'] = logic_list[i].get('game_logic_passed', False)
            if 'game_logic_error' in logic_list[i]:
                full_list[i]['game_logic_error'] = logic_list[i]['game_logic_error']
            
            merged_count += 1
    
    # Save merged results
    with open(output_file, 'w') as f:
        json.dump(full_results, f, indent=2)
    
    print(f"Merged {merged_count}/{total_count} results")
    print(f"Saved to: {output_file}")
    print()
    
    return True

def update_matrix(full_results_file, matrix_file):
    """Update results matrix with game logic counts"""
    
    results = load_json_file(full_results_file)
    if results is None:
        return False
    
    matrix = {}
    for game_name, game_data in results.items():
        if 'gemini' not in game_data:
            continue
        
        matrix[game_name] = {}
        matrix[game_name]['gemini'] = {
            'syntax': sum(1 for r in game_data['gemini'] if r.get('syntax_passed', False)),
            'semantic': sum(1 for r in game_data['gemini'] if r.get('semantic_passed', False)),
            'game_logic': sum(1 for r in game_data['gemini'] if r.get('game_logic_passed', False))
        }
    
    with open(matrix_file, 'w') as f:
        json.dump(matrix, f, indent=2)
    
    print(f"Matrix updated: {matrix_file}")
    print()
    
    # Print summary
    print("="*70)
    print("UPDATED RESULTS MATRIX")
    print("="*70)
    for game_name, game_data in matrix.items():
        print(f"{game_name}:")
        for model_name, counts in game_data.items():
            print(f"  {model_name}:")
            print(f"    Syntax: {counts['syntax']}")
            print(f"    Semantic: {counts['semantic']}")
            print(f"    Game Logic: {counts['game_logic']}")
    print("="*70)
    
    return True

def main():
    # Find latest files
    full_files = glob.glob("experiment_results_full_*.json")
    logic_files = glob.glob("experiment_results_with_logic_*.json")
    
    if not full_files:
        print("No experiment_results_full_*.json files found")
        return
    
    if not logic_files:
        print("No experiment_results_with_logic_*.json files found")
        return
    
    # Use the specified full results file
    full_results_file = "experiment_results_full_gemini.json"
    if not os.path.exists(full_results_file):
        full_results_file = max(full_files, key=os.path.getctime)
    
    # Use latest logic results
    logic_results_file = max(logic_files, key=os.path.getctime)
    
    # Output file
    output_file = full_results_file.replace('.json', '_merged.json')
    
    # Merge results
    if merge_game_logic_results(full_results_file, logic_results_file, output_file):
        # Update matrix
        update_matrix(output_file, "results_matrix.json")
        
        # Also update the original full results file
        print("\nUpdating original full results file...")
        with open(output_file, 'r') as f:
            merged_data = json.load(f)
        with open(full_results_file, 'w') as f:
            json.dump(merged_data, f, indent=2)
        print(f"Updated: {full_results_file}")
    
    print("\n✅ Merge complete!")

if __name__ == '__main__':
    main()

