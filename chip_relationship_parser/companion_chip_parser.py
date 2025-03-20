import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Tuple, List
from urllib.parse import urljoin
import os

def get_parts(url) -> Tuple[List[str], List[str], List[str]]:
    """
    Extract companion parts, alternative parts, and catalog hierarchy from an Analog Devices product page.
    
    Args:
        url (str): The URL of the Analog Devices product page
        
    Returns:
        Tuple[List[str], List[str], List[str]]: A tuple containing (companion_parts, alternative_parts, catalog_hierarchy)
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Save the HTML response for inspection
        output_dir = "debug_output"
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "ad5314.html"), "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"\nSaved HTML to: {os.path.join(output_dir, 'ad5314.html')}")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        def extract_product_links(tab_id: str) -> List[str]:
            """Extract product links from a tab content."""
            product_links = []
            
            # Find the tab panel by ID
            tab_panel = soup.find('div', {'id': tab_id, 'role': 'tabpanel'})
            if not tab_panel:
                return product_links
                
            # Find all links in the tab
            for link in tab_panel.find_all('a', href=True):
                href = link['href']
                # Check if it's a product link
                if '/en/products/' in href and href.endswith('.html'):
                    # Extract the product name from the URL
                    product_name = href.split('/')[-1].replace('.html', '')
                    product_links.append(product_name)
            
            return product_links
        
        def extract_catalog_hierarchy() -> List[str]:
            """Extract the catalog hierarchy from the breadcrumb navigation."""
            hierarchy = []
            
            # Find the breadcrumb container
            breadcrumb_container = soup.find('div', {'class': 'breadcrumb__container'})
            if not breadcrumb_container:
                return hierarchy
            
            # Find all sections in the breadcrumb
            for section in breadcrumb_container.find_all('div', {'class': 'breadcrumb__container__section'}):
                # Try to find a link first
                link = section.find('a')
                if link:
                    # Get text from the span inside the link
                    span = link.find('span')
                    if span:
                        hierarchy.append(span.get_text().strip())
                    else:
                        hierarchy.append(link.get_text().strip())
                else:
                    # If no link, get the direct text
                    text = section.get_text().strip()
                    if text:
                        hierarchy.append(text)
            
            return hierarchy
        
        # Debug: Print all tab-like elements
        print("\nDebug: Looking for tab elements...")
        for element in soup.find_all(['div', 'section', 'tab-panel', 'tabpanel']):
            if element.get('role') == 'tabpanel' or 'tab' in element.get('class', []):
                print(f"Found tab element: {element.get('id', 'no-id')} - {element.get('aria-label', 'no-label')}")
                print(f"Classes: {element.get('class', [])}")
                print(f"Content preview: {element.get_text()[:100]}...\n")
        
        # Extract parts from each tab using their specific IDs
        companion_parts = extract_product_links('tab-panel-companionParts')
        alternative_parts = extract_product_links('tab-panel-alternativeParts')
        catalog_hierarchy = extract_catalog_hierarchy()
        
        print("\nDebug: Companion tab found:", bool(companion_parts))
        print("Debug: Alternative tab found:", bool(alternative_parts))
        print("Debug: Catalog hierarchy found:", bool(catalog_hierarchy))
        
        return companion_parts, alternative_parts, catalog_hierarchy
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return [], [], []
    except Exception as e:
        print(f"Error parsing parts: {e}")
        print(f"Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return [], [], []

def main():
    # Example usage
    url = "https://www.analog.com/en/products/ad5314.html"
    print(f"Fetching parts from: {url}")
    
    companion_parts, alternative_parts, catalog_hierarchy = get_parts(url)
    
    if catalog_hierarchy:
        print("\nCatalog Hierarchy:")
        print(" > ".join(catalog_hierarchy))
        print(f"\nTotal hierarchy levels: {len(catalog_hierarchy)}")
    else:
        print("\nNo catalog hierarchy found")
    
    if companion_parts:
        print("\nCompanion Parts:")
        for part in companion_parts:
            print(f"- {part}")
        print(f"\nTotal companion parts found: {len(companion_parts)}")
    else:
        print("\nNo companion parts found")
        
    if alternative_parts:
        print("\nAlternative Parts:")
        for part in alternative_parts:
            print(f"- {part}")
        print(f"\nTotal alternative parts found: {len(alternative_parts)}")
    else:
        print("\nNo alternative parts found")

if __name__ == "__main__":
    main()
