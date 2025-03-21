import json

def add_leaf_property(node):
    """
    Recursively add the leaf property to all nodes in the tree.
    A node is a leaf if it has no subcategories or an empty subcategories array.
    """
    # Add leaf property based on subcategories
    node['leaf'] = not node.get('subcategories') or len(node['subcategories']) == 0
    
    # Recursively process subcategories if they exist
    if node.get('subcategories'):
        for subcategory in node['subcategories']:
            add_leaf_property(subcategory)

def main():
    # Read the input JSON file
    with open('chip_relationship_parser/catalog_tree.json', 'r') as f:
        tree = json.load(f)
    
    # Add leaf property to all nodes
    add_leaf_property(tree)
    
    # Write the modified tree to a new file
    with open('chip_relationship_parser/catalog_tree_annotated.json', 'w') as f:
        json.dump(tree, f, indent=2)

if __name__ == '__main__':
    main() 