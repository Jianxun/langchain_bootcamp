#!/usr/bin/env python3

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global variables
visited_urls: Set[str] = set()
processed_urls: Set[str] = set()
MAX_PAGES = 50  # Maximum number of pages to process
DELAY_BETWEEN_REQUESTS = 2  # Delay in seconds between requests

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Parse solutions from Analog Devices website')
    parser.add_argument('url', help='URL to start parsing from')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum number of pages to process')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests in seconds')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum recursion depth')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    return parser.parse_args()

def normalize_url(url: str) -> str:
    """
    Normalize URL to ensure it has the correct prefix.
    
    Args:
        url (str): URL to normalize
        
    Returns:
        str: Normalized URL with correct prefix
    """
    if not url:
        return ""
        
    # If URL is relative, add the base prefix
    if url.startswith('/'):
        url = f"https://www.analog.com{url}"
    # If URL doesn't have a scheme, add https
    elif not url.startswith(('http://', 'https://')):
        url = f"https://www.analog.com/{url}"
    # If URL doesn't have www, add it
    elif url.startswith('https://analog.com'):
        url = url.replace('https://analog.com', 'https://www.analog.com')
    elif url.startswith('http://analog.com'):
        url = url.replace('http://analog.com', 'https://www.analog.com')
    elif url.startswith('https://www.analog.com') or url.startswith('http://www.analog.com'):
        # Already has www, just ensure https
        url = url.replace('http://', 'https://')
    else:
        # For any other URL, ensure it starts with https://www.analog.com
        url = f"https://www.analog.com/{url}"
        
    return url

def is_valid_solution_url(url: str) -> bool:
    """
    Check if the URL is a valid solution URL from Analog Devices.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        url = normalize_url(url)
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

def fetch_html(url: str, timeout: int = 30) -> str:
    """
    Fetch HTML content from a URL using requests with retries.
    
    Args:
        url (str): URL to fetch HTML from
        timeout (int): Timeout in seconds
        
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
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Check if we got a valid HTML response
            if 'text/html' not in response.headers.get('Content-Type', ''):
                logger.warning(f"Unexpected content type: {response.headers.get('Content-Type')}")
            
            return response.text
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching {url} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                logger.info(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response content: {e.response.text[:500]}...")  # Log first 500 chars of error response
            if attempt < max_retries - 1:
                logger.info(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                
    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
    return ""

def parse_solution_description(url: str, timeout: int = 30) -> str:
    """
    Fetch and parse the description from a solution's page.
    
    Args:
        url (str): URL of the solution page or path to local HTML file
        timeout (int): Timeout in seconds
        
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
        else:
            # Create a session with retry logic
            session = create_session()
            
            # Fetch the page with timeout and retries
            content = fetch_html(url, timeout)
            if not content:
                logger.error(f"Failed to fetch content from {url}")
                return ""
                
        # Parse the HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Debug: Save the HTML content
        debug_file = Path(__file__).parent / f"debug_description_{len(processed_urls)}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        logger.info(f"Saved description HTML to {debug_file}")
        
        # Look for the adi-rte div which contains the main content
        adi_rte = soup.find('div', class_='adi-rte')
        if adi_rte:
            logger.info("Found adi-rte div")
            description = []
            
            # Print the raw HTML for debugging
            logger.debug("\nRaw HTML found:")
            logger.debug("-" * 80)
            logger.debug(adi_rte.prettify())
            logger.debug("-" * 80)
            
            # Find all paragraphs
            paragraphs = adi_rte.find_all('p')
            logger.info(f"Found {len(paragraphs)} paragraphs")
            
            # Process each paragraph
            for i, p in enumerate(paragraphs, 1):
                logger.debug(f"\nParagraph {i}:")
                logger.debug("-" * 40)
                
                # Get the raw text with <br> tags
                raw_html = str(p)
                logger.debug("Raw HTML:")
                logger.debug(raw_html)
                
                # Split on double <br> tags
                parts = raw_html.split('<br/>\n<br/>')
                logger.debug(f"\nSplit into {len(parts)} parts")
                
                # Process each part
                for j, part in enumerate(parts, 1):
                    # Parse the part as HTML to handle any remaining tags
                    part_soup = BeautifulSoup(part, 'html.parser')
                    text = part_soup.get_text(strip=True)
                    
                    if text:  # Skip empty parts
                        logger.debug(f"\nPart {j}:")
                        logger.debug(f"Length: {len(text)} chars")
                        logger.debug(text)
                        description.append(text)
            
            # Join all parts with proper spacing
            full_description = '\n\n'.join(description)
            
            # Print statistics
            logger.info(f"Description length: {len(full_description)} characters")
            logger.info(f"Number of words: {len(full_description.split())}")
            logger.info(f"Number of paragraphs: {len(description)}")
            
            return full_description
            
        # Fallback: Try meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            logger.info("Found description in meta tags")
            return meta_desc['content']
            
        # If we still haven't found anything, try to get all text
        logger.info("Trying to get all text content")
        text = soup.get_text(separator='\n', strip=True)
        if text:
            # Split into paragraphs and filter out short ones
            paragraphs = [p for p in text.split('\n') if len(p.strip()) > 50]
            if paragraphs:
                logger.info(f"Found {len(paragraphs)} paragraphs from all text")
                return '\n\n'.join(paragraphs)
                
        logger.warning(f"No description found for {url}")
        return ""
        
    except Exception as e:
        logger.error(f"Error parsing description from {url}: {str(e)}")
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

def load_partial_results() -> List[Dict[str, str]]:
    """Load partial results if they exist."""
    script_dir = Path(__file__).parent
    partial_file = script_dir / "parsed_solutions_partial.json"
    if partial_file.exists():
        with open(partial_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
            # Mark URLs as visited
            for solution in results:
                visited_urls.add(solution['link'])
                if 'sub_solutions' in solution:
                    for sub in solution['sub_solutions']:
                        visited_urls.add(sub['link'])
            logger.info(f"Loaded {len(results)} solutions from partial results")
            return results
    return []

def save_partial_results(solutions: List[Dict[str, str]]):
    """Save partial results."""
    script_dir = Path(__file__).parent
    output_file = script_dir / "parsed_solutions_partial.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(solutions, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(solutions)} solutions to {output_file}")

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
    # Normalize the URL
    url = normalize_url(url)
    
    # Skip if we've already visited this URL or reached max depth
    if url in visited_urls or depth >= max_depth:
        return []
    
    # Check if we've reached the maximum number of pages
    if len(processed_urls) >= MAX_PAGES:
        logger.warning(f"Reached maximum number of pages ({MAX_PAGES})")
        return []
    
    visited_urls.add(url)
    processed_urls.add(url)
    
    # Add delay between requests
    time.sleep(DELAY_BETWEEN_REQUESTS)
    
    content = fetch_html(url)
    if not content:
        return []
        
    soup = BeautifulSoup(content, 'html.parser')
    solutions = []
    
    # Debug: Save the HTML content
    debug_file = Path(__file__).parent / f"debug_content_{depth}_{len(visited_urls)}.html"
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Saved HTML content to {debug_file}")
    
    # Print some debug information about the page
    title = soup.title.string if soup.title else "No title found"
    logger.info(f"Parsing page at depth {depth}: {title}")
    
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
        logger.info(f"Found {len(sections)} sections with {tag}{f'.{class_name}' if class_name else ''}")
        
        # Process one section at a time
        for i, section in enumerate(sections, 1):
            logger.info(f"Processing section {i}/{len(sections)}")
            
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
            if link_elem and 'href' in link_elem.attrs:
                link = urljoin(url, link_elem['href'])
                link = normalize_url(link)  # Normalize the link
            else:
                link = ""
            
            # Skip if link doesn't contain "/en/solutions" or title starts with "Back to"
            if not link or "/en/solutions" not in link or title.startswith("Back to"):
                continue
            
            # Get the image and make it absolute
            img_elem = section.find('img')
            if img_elem and 'src' in img_elem.attrs:
                image_url = urljoin(url, img_elem['src'])
                image_url = normalize_url(image_url)  # Normalize the image URL
            else:
                image_url = ""
            
            # Get description from the solution's own page
            logger.info(f"Fetching description for: {title}")
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
                logger.info(f"Found solution: {title}")
                
                # Save progress after each solution
                save_partial_results(solutions)
                
                # Recursively parse sub-solutions if we have a valid link
                if link and is_valid_solution_url(link):
                    logger.info(f"Following link to sub-solutions: {link}")
                    sub_solutions = parse_solutions(link, depth + 1, max_depth)
                    if sub_solutions:
                        solution['sub_solutions'] = sub_solutions
    
    return solutions

def main():
    args = parse_args()
    
    # Update global variables from command line arguments
    global MAX_PAGES, DELAY_BETWEEN_REQUESTS
    MAX_PAGES = args.max_pages
    DELAY_BETWEEN_REQUESTS = args.delay
    
    url = args.url
    logger.info(f"Starting to parse solutions from {url}")
    logger.info(f"Max pages: {MAX_PAGES}, Delay: {DELAY_BETWEEN_REQUESTS}s, Max depth: {args.max_depth}")
    
    try:
        # Load partial results if they exist
        solutions = load_partial_results()
        
        # Parse new solutions
        new_solutions = parse_solutions(url, max_depth=args.max_depth)
        solutions.extend(new_solutions)
        
        # Print solutions in a readable format
        logger.info(f"Found {len(solutions)} Solutions from {url}")
        for solution in solutions:
            logger.info(f"\nTitle: {solution['title']}")
            logger.info(f"Description: {solution['description'][:200]}...")  # Truncate long descriptions
            logger.info(f"Link: {solution['link']}")
            logger.info(f"Image URL: {solution['image_url']}")
            logger.info(f"Depth: {solution['depth']}")
            if 'sub_solutions' in solution:
                logger.info(f"Sub-solutions: {len(solution['sub_solutions'])}")
        
        # Save to JSON file in solutions folder
        script_dir = Path(__file__).parent
        output_file = script_dir / "parsed_solutions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(solutions, f, indent=2, ensure_ascii=False)
        logger.info(f"Solutions saved to {output_file}")
        
    except KeyboardInterrupt:
        logger.info("Script interrupted by user. Saving progress...")
        # Save partial results if we have any
        if 'solutions' in locals() and solutions:
            save_partial_results(solutions)
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_parse_description()
    else:
        main() 