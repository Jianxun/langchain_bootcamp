#!/usr/bin/env python3

import os
import sys
import json
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global set to track visited URLs
visited_urls: Set[str] = set()

def is_valid_solution_url(url: str) -> bool:
    """
    Check if the URL is a valid solution URL from Analog Devices.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        # Check if it's an analog.com URL
        if not parsed.netloc.endswith('analog.com'):
            return False
        # Check if it's a solutions page
        if '/solutions/' not in parsed.path:
            return False
        # Exclude certain paths
        if any(x in parsed.path for x in ['/media-center/', '/videos/', '/index.html']):
            return False
        return True
    except:
        return False

def create_session() -> requests.Session:
    """Create a requests session with retry strategy."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_html(url: str) -> str:
    """
    Fetch HTML content from a URL using requests with retries.
    
    Args:
        url (str): URL to fetch HTML from
        
    Returns:
        str: HTML content
    """
    session = create_session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        logger.info(f"Fetching {url}")
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if we got a valid HTML response
        if 'text/html' not in response.headers.get('Content-Type', ''):
            logger.warning(f"Unexpected content type: {response.headers.get('Content-Type')}")
        
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {str(e)}")
        if hasattr(e.response, 'text'):
            logger.error(f"Response content: {e.response.text[:500]}...")  # Log first 500 chars of error response
        return ""

def parse_solution_description(url: str) -> str:
    """
    Fetch and parse the description from a solution's page.
    
    Args:
        url (str): URL of the solution page or path to local HTML file
        
    Returns:
        str: Description of the solution
    """
    try:
        # Check if this is a local file
        if url.startswith('file://') or not url.startswith(('http://', 'https://')):
            # Remove file:// prefix if present
            file_path = url.replace('file://', '')
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
        else:
            # Create a session with retry logic
            session = create_session()
            
            # Fetch the page
            response = session.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
        
        # First try to find description in meta tags
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
            
        # Look for the adi-rte div which contains the main content
        adi_rte = soup.find('div', class_='adi-rte')
        if adi_rte:
            description = []
            for p in adi_rte.find_all('p'):
                # Get the raw HTML and split on double <br> tags
                raw_html = str(p)
                parts = raw_html.split('<br/>\n<br/>')
                
                # Process each part
                for part in parts:
                    # Parse the part as HTML to handle any remaining tags
                    part_soup = BeautifulSoup(part, 'html.parser')
                    text = part_soup.get_text(strip=True)
                    if text:  # Skip empty parts
                        description.append(text)
            
            return '\n\n'.join(description)
        
        # Fallback: Look for any paragraph with substantial content
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 100:  # Look for substantial paragraphs
                return text
                
        return ""
        
    except Exception as e:
        print(f"Error parsing description from {url}: {str(e)}")
        return ""

def test_parse_description():
    """Test parsing description from ADEF_radar.html"""
    script_dir = Path(__file__).parent
    test_file = script_dir / "ADEF_radar.html"
    
    if not test_file.exists():
        print(f"Error: {test_file} not found")
        return
        
    print("\nTesting description parsing from ADEF_radar.html:")
    print("=" * 80)
    
    # Read the file content directly
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find the adi-rte div
    adi_rte = soup.find('div', class_='adi-rte')
    if not adi_rte:
        print("Error: Could not find div.adi-rte")
        return
        
    # Print the raw HTML for debugging
    print("\nRaw HTML found:")
    print("-" * 80)
    print(adi_rte.prettify())
    print("-" * 80)
    
    # Find all paragraphs
    paragraphs = adi_rte.find_all('p')
    print(f"\nFound {len(paragraphs)} paragraphs")
    
    # Process each paragraph
    description = []
    for i, p in enumerate(paragraphs, 1):
        print(f"\nParagraph {i}:")
        print("-" * 40)
        
        # Get the raw text with <br> tags
        raw_html = str(p)
        print("Raw HTML:")
        print(raw_html)
        
        # Split on double <br> tags
        parts = raw_html.split('<br/>\n<br/>')
        print(f"\nSplit into {len(parts)} parts")
        
        # Process each part
        for j, part in enumerate(parts, 1):
            # Parse the part as HTML to handle any remaining tags
            part_soup = BeautifulSoup(part, 'html.parser')
            text = part_soup.get_text(strip=True)
            
            if text:  # Skip empty parts
                print(f"\nPart {j}:")
                print(f"Length: {len(text)} chars")
                print(text)
                description.append(text)
    
    # Join all parts with proper spacing
    full_description = '\n\n'.join(description)
    
    # Print the final result
    print("\nFinal description:")
    print("-" * 80)
    print(full_description)
    print("-" * 80)
    
    # Print statistics
    print(f"\nDescription length: {len(full_description)} characters")
    print(f"Number of words: {len(full_description.split())}")
    print(f"Number of paragraphs: {len(description)}")

def parse_solutions(url: str, depth: int = 0, max_depth: int = 3) -> List[Dict[str, str]]:
    """
    Parse the solutions information from a URL recursively.
    
    Args:
        url (str): URL to fetch and parse solutions from
        depth (int): Current recursion depth
        max_depth (int): Maximum recursion depth
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing solution information
    """
    # Skip if we've already visited this URL or reached max depth
    if url in visited_urls or depth >= max_depth:
        return []
    
    visited_urls.add(url)
    content = fetch_html(url)
    if not content:
        return []
        
    soup = BeautifulSoup(content, 'html.parser')
    solutions = []
    
    # Debug: Save the HTML content
    debug_file = Path(__file__).parent / f"debug_content_{depth}_{len(visited_urls)}.html"
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved HTML content to {debug_file}")
    
    # Print some debug information about the page
    title = soup.title.string if soup.title else "No title found"
    print(f"\nParsing page at depth {depth}: {title}")
    
    # Try different selectors for solution sections
    selectors = [
        ('div', 'right-container-top'),
        ('div', 'tabs-option'),
        ('div', 'explore-applications__container__tabs-options'),
        ('div', 'content-and-cta'),
        ('div', 'card'),
        ('div', 'solution-card'),
        ('div', 'solution'),
        ('article', None),
        ('div', 'product-card'),
        ('div', 'application-card')
    ]
    
    for tag, class_name in selectors:
        if class_name:
            sections = soup.find_all(tag, class_=class_name)
        else:
            sections = soup.find_all(tag)
        print(f"\nFound {len(sections)} sections with {tag}{f'.{class_name}' if class_name else ''}")
        
        for section in sections:
            # Try different title selectors
            title = None
            title_selectors = [
                'h3.title-small', 
                'span.body-small', 
                '.title-small', 
                'span.subtitle-medium',
                'h2', 'h3', 'h4',  # Try any heading
                '.title', '.heading',  # Try generic title/heading classes
                'a',  # Try links as titles
                '.product-title',  # Try product titles
                '.application-title'  # Try application titles
            ]
            for title_selector in title_selectors:
                title_elem = section.select_one(title_selector)
                if title_elem:
                    title = title_elem.text.strip()
                    break
            
            if not title:
                continue
                
            # Get the link and make it absolute
            link_elem = section.find('a')
            link = urljoin(url, link_elem['href']) if link_elem and 'href' in link_elem.attrs else ""
            
            # Skip if link doesn't contain "/en/solutions" or title starts with "Back to"
            if not link or "/en/solutions" not in link or title.startswith("Back to"):
                continue
            
            # Get the image and make it absolute
            img_elem = section.find('img')
            image_url = urljoin(url, img_elem['src']) if img_elem and 'src' in img_elem.attrs else ""
            
            # Get description from the solution's own page
            description = parse_solution_description(link)
            
            solution = {
                'title': title,
                'description': description,
                'link': link,
                'image_url': image_url,
                'depth': depth,
                'parent_url': url
            }
            
            # Only add if we haven't seen this title before
            if not any(s['title'] == title for s in solutions):
                solutions.append(solution)
                print(f"Found solution: {title}")
                
                # Recursively parse sub-solutions if we have a valid link
                if link and is_valid_solution_url(link):
                    print(f"Following link to sub-solutions: {link}")
                    sub_solutions = parse_solutions(link, depth + 1, max_depth)
                    if sub_solutions:
                        solution['sub_solutions'] = sub_solutions
    
    return solutions

def main():
    if len(sys.argv) != 2:
        print("Usage: python parse_solutions.py <url>")
        print("Example: python parse_solutions.py https://www.analog.com/en/solutions.html")
        sys.exit(1)
        
    url = sys.argv[1]
    solutions = parse_solutions(url)
    
    # Print solutions in a readable format
    print(f"\nFound {len(solutions)} Solutions from {url}:")
    print("-" * 80)
    for solution in solutions:
        print(f"\nTitle: {solution['title']}")
        print(f"Description: {solution['description'][:200]}...")  # Truncate long descriptions
        print(f"Link: {solution['link']}")
        print(f"Image URL: {solution['image_url']}")
        print(f"Depth: {solution['depth']}")
        if 'sub_solutions' in solution:
            print(f"Sub-solutions: {len(solution['sub_solutions'])}")
        print("-" * 80)
    
    # Save to JSON file in solutions folder
    script_dir = Path(__file__).parent
    output_file = script_dir / "parsed_solutions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(solutions, f, indent=2, ensure_ascii=False)
    print(f"\nSolutions saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_parse_description()
    else:
        main() 