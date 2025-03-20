import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set
import json
import os
import time
from urllib.parse import urljoin

class CatalogParser:
    def __init__(self, base_url: str = "https://www.analog.com"):
        """
        Initialize the catalog parser.
        
        Args:
            base_url (str): The base URL of the Analog Devices website
        """
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Create output directory
        self.output_dir = "catalog_output"
        os.makedirs(self.output_dir, exist_ok=True)
        # Track visited URLs and category data
        self.visited_urls: Set[str] = set()
        self.category_data_map: Dict[str, Dict] = {}
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage.
        
        Args:
            url (str): The URL to fetch
            
        Returns:
            Optional[BeautifulSoup]: The parsed page or None if failed
        """
        try:
            # Add delay to be nice to the server
            time.sleep(1)
            
            print(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save the HTML response for inspection
            page_name = url.split('/')[-1].replace('.html', '') or 'index'
            with open(os.path.join(self.output_dir, f"{page_name}.html"), "w", encoding="utf-8") as f:
                f.write(response.text)
            
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def get_or_create_category(self, url: str, name: str, parent_path: List[str]) -> Dict:
        """
        Get existing category data or create new category data.
        
        Args:
            url (str): The category URL
            name (str): The category name
            parent_path (List[str]): The path of parent categories
            
        Returns:
            Dict: The category data
        """
        if url in self.category_data_map:
            category_data = self.category_data_map[url]
            # Add new parent path if not already present
            if parent_path not in category_data['parent_paths']:
                category_data['parent_paths'].append(parent_path)
            return category_data
        
        category_data = {
            'name': name,
            'url': url,
            'parent_paths': [parent_path],
            'subcategories': [],
            'description': ''
        }
        self.category_data_map[url] = category_data
        return category_data
    
    def parse_category_page(self, url: str, parent_path: List[str] = None) -> Optional[Dict]:
        """
        Parse a category page and its subcategories recursively.
        
        Args:
            url (str): The URL of the category page
            parent_path (List[str]): The path of parent categories
            
        Returns:
            Optional[Dict]: The category data or None if already visited
        """
        if parent_path is None:
            parent_path = []
            
        # Skip if already visited
        if url in self.visited_urls:
            return self.category_data_map.get(url)
            
        self.visited_urls.add(url)
        soup = self.get_page(url)
        if not soup:
            return None
            
        # Get the category name from breadcrumb or title
        name = ''
        breadcrumb = soup.find('div', {'class': 'breadcrumb__container'})
        if breadcrumb:
            sections = breadcrumb.find_all('div', {'class': 'breadcrumb__container__section'})
            if sections:
                name = sections[-1].get_text().strip()
        
        if not name:
            title = soup.find('title')
            if title:
                name = title.get_text().strip()
        
        print(f"\nParsing category: {name}")
        
        # Get or create category data
        category_data = self.get_or_create_category(url, name, parent_path)
        
        # Find subcategories - handle both main product page and category pages
        if 'product-category.html' in url:
            # Main product page structure
            category_list = soup.find('ul', {'class': 'list-sort-unstyled'})
            if category_list:
                for category_link in category_list.find_all('a', {'class': 'text-link'}):
                    href = category_link.get('href')
                    if href and '/product-category/' in href:
                        full_url = urljoin(self.base_url, href)
                        name = category_link.get_text().strip()
                        if name and full_url != url:  # Avoid self-references
                            print(f"Found main category: {name} at {full_url}")
                            new_path = parent_path + [category_data['name']]
                            subcategory_data = self.parse_category_page(full_url, new_path)
                            if subcategory_data:
                                category_data['subcategories'].append(subcategory_data)
        else:
            # Look for subcategory cards
            subcategory_cards = soup.find_all('div', {'class': 'subcategories-container__item'})
            if subcategory_cards:
                print(f"Found {len(subcategory_cards)} subcategory cards")
                for card in subcategory_cards:
                    # Find the title link in the card
                    title_link = card.find('a', {'class': 'title-link'})
                    if title_link and '/product-category/' in title_link.get('href', ''):
                        href = title_link.get('href')
                        full_url = urljoin(self.base_url, href)
                        
                        # Get the title
                        title_elem = title_link.find('h3', {'class': 'subcategory-left__titles__title'})
                        if title_elem:
                            name = title_elem.get_text().strip()
                            
                            # Get the description
                            desc_elem = card.find('div', {'class': 'subcategory-left__titles__subtitle'})
                            description = desc_elem.get_text().strip() if desc_elem else ''
                            
                            if name and full_url != url:  # Avoid self-references
                                print(f"Found subcategory card: {name}")
                                new_path = parent_path + [category_data['name']]
                                subcategory_data = self.parse_category_page(full_url, new_path)
                                if subcategory_data:
                                    # Add description to the subcategory data
                                    subcategory_data['description'] = description
                                    category_data['subcategories'].append(subcategory_data)
            
            # Also look for sub-subcategories in the content body
            sub_subcategories = soup.find_all('a', {'class': 'subcategory-content-body__link'})
            if sub_subcategories:
                print(f"Found {len(sub_subcategories)} sub-subcategories")
                for link in sub_subcategories:
                    href = link.get('href')
                    if href and '/product-category/' in href:
                        full_url = urljoin(self.base_url, href)
                        # Get the text from the paragraph element inside the link
                        text_elem = link.find('p', {'class': 'subcategory-content-body__link__text'})
                        name = text_elem.get_text().strip() if text_elem else link.get_text().strip()
                        
                        if name and full_url != url:  # Avoid self-references
                            print(f"Found sub-subcategory: {name}")
                            new_path = parent_path + [category_data['name']]
                            subcategory_data = self.parse_category_page(full_url, new_path)
                            if subcategory_data:
                                category_data['subcategories'].append(subcategory_data)
        
        return category_data
    
    def save_catalog_tree(self, catalog_tree: Dict, filename: str = "catalog_tree.json"):
        """
        Save the catalog tree to a JSON file.
        
        Args:
            catalog_tree (Dict): The catalog tree structure
            filename (str): The output filename
        """
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_tree, f, indent=2, ensure_ascii=False)
        print(f"\nCatalog tree saved to: {output_path}")
    
    def print_catalog_tree(self, catalog_tree: Dict, indent: int = 0, visited: Set[str] = None):
        """
        Print the catalog tree in a hierarchical format.
        
        Args:
            catalog_tree (Dict): The catalog tree structure
            indent (int): The current indentation level
            visited (Set[str]): Set of visited URLs to avoid cycles
        """
        if not catalog_tree:
            return
            
        if visited is None:
            visited = set()
            
        # Skip if already visited to avoid cycles
        if catalog_tree['url'] in visited:
            return
            
        visited.add(catalog_tree['url'])
        
        line = "  " * indent + "- " + catalog_tree['name']
        if 'description' in catalog_tree:
            # Add first 100 chars of description if available
            desc = catalog_tree['description'][:100] + "..." if len(catalog_tree['description']) > 100 else catalog_tree['description']
            line += f" ({desc})"
        print(line)
        
        for subcategory in catalog_tree['subcategories']:
            self.print_catalog_tree(subcategory, indent + 1, visited)

def main():
    # Initialize parser
    parser = CatalogParser()
    
    # Start URL for product categories
    start_url = "https://www.analog.com/en/product-category.html"
    
    print("Starting catalog crawl...")
    catalog_tree = parser.parse_category_page(start_url)
    
    print("\nCatalog Tree Structure:")
    parser.print_catalog_tree(catalog_tree)
    
    # Save the results
    parser.save_catalog_tree(catalog_tree)

if __name__ == "__main__":
    main() 