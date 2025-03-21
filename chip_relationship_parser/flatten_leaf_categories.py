import json
import os
from typing import Dict, List

def flatten_leaf_categories(catalog_tree: Dict, output_file: str):
    """
    Flatten the catalog tree into a JSONL file, keeping only leaf nodes.
    
    Args:
        catalog_tree (Dict): The annotated catalog tree structure with leaf property
        output_file (str): Path to the output JSONL file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        def process_category(category: Dict):
            # If this is a leaf node, write it to the output file
            if category.get('leaf', False):
                # Create a flattened entry with essential information
                flattened_entry = {
                    'name': category['name'],
                    'url': category['url'],
                    'parent_paths': category['parent_paths'],
                    'description': category.get('description', ''),
                    'level': len(category['parent_paths'][0]) if category['parent_paths'] else 0
                }
                
                # Write the entry as a JSON line
                f.write(json.dumps(flattened_entry, ensure_ascii=False) + '\n')
            
            # Process subcategories recursively
            for subcategory in category.get('subcategories', []):
                process_category(subcategory)
        
        # Start processing from the root
        process_category(catalog_tree)

def main():
    # Input and output paths
    input_file = "chip_relationship_parser/catalog_tree_annotated.json"
    output_file = "chip_relationship_parser/flattened_leaf_categories.jsonl"
    
    # Read the annotated catalog tree
    with open(input_file, 'r', encoding='utf-8') as f:
        catalog_tree = json.load(f)
    
    # Flatten the catalog, keeping only leaf nodes
    flatten_leaf_categories(catalog_tree, output_file)
    print(f"Flattened leaf categories saved to: {output_file}")
    
    # Print some statistics
    with open(output_file, 'r', encoding='utf-8') as f:
        categories = [json.loads(line) for line in f]
    
    print(f"\nStatistics:")
    print(f"Total leaf categories: {len(categories)}")
    print(f"Maximum hierarchy depth: {max(cat['level'] for cat in categories)}")
    print(f"Categories with multiple parent paths: {sum(1 for cat in categories if len(cat['parent_paths']) > 1)}")
    
    # Print a sample of leaf categories
    print("\nSample leaf categories:")
    for cat in categories[:5]:
        print(f"- {cat['name']} (Level: {cat['level']})")

if __name__ == "__main__":
    main() 