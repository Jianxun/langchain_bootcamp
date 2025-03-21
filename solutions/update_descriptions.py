#!/usr/bin/env python3

import os
import sys
import json
import time
from typing import List, Dict
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

# Global variables
DELAY_BETWEEN_REQUESTS = 2  # Delay in seconds between requests

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

def parse_solution_description(url: str, content: str, debug_dir: Path) -> str:
    """
    Parse the description from a solution's page.
    
    Args:
        url (str): URL of the solution page
        content (str): HTML content of the page
        debug_dir (Path): Directory to save debug files
        
    Returns:
        str: Description of the solution
    """
    try:
        # Parse the HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Debug: Save the HTML content
        debug_file = debug_dir / f"debug_description_{len(os.listdir(debug_dir))}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        logger.info(f"Saved description HTML to {debug_file}")
        
        # Look for the adi-rte div which contains the main content
        adi_rte = soup.find('div', class_='adi-rte')
        if adi_rte:
            logger.info("Found adi-rte div")
            description = []
            
            # Find all paragraphs
            paragraphs = adi_rte.find_all('p')
            logger.info(f"Found {len(paragraphs)} paragraphs")
            
            # Process each paragraph
            for i, p in enumerate(paragraphs, 1):
                # Get the raw text with <br> tags
                raw_html = str(p)
                
                # Split on double <br> tags
                parts = raw_html.split('<br/>\n<br/>')
                
                # Process each part
                for part in parts:
                    # Parse the part as HTML to handle any remaining tags
                    part_soup = BeautifulSoup(part, 'html.parser')
                    text = part_soup.get_text(strip=True)
                    
                    if text:  # Skip empty parts
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

def process_solution(solution: Dict, debug_dir: Path) -> Dict:
    """
    Process a single solution by fetching and parsing its description.
    
    Args:
        solution (Dict): Solution dictionary
        debug_dir (Path): Directory to save debug files
        
    Returns:
        Dict: Updated solution dictionary
    """
    url = solution['link']
    logger.info(f"Processing solution: {solution['title']}")
    
    # Add delay between requests
    time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Fetch the page content
    content = fetch_html(url)
    if not content:
        logger.error(f"Failed to fetch content for {url}")
        return solution
        
    # Parse the description
    new_description = parse_solution_description(url, content, debug_dir)
    if new_description:
        solution['description'] = new_description
        logger.info(f"Updated description for {solution['title']}")
    else:
        logger.warning(f"Could not update description for {solution['title']}")
        
    return solution

def process_solutions_recursive(solutions: List[Dict], debug_dir: Path) -> List[Dict]:
    """
    Process all solutions recursively, including sub-solutions.
    
    Args:
        solutions (List[Dict]): List of solutions to process
        debug_dir (Path): Directory to save debug files
        
    Returns:
        List[Dict]: Updated list of solutions
    """
    processed_solutions = []
    for solution in solutions:
        # Process the current solution
        solution = process_solution(solution, debug_dir)
        
        # Process sub-solutions if they exist
        if 'sub_solutions' in solution:
            solution['sub_solutions'] = process_solutions_recursive(solution['sub_solutions'], debug_dir)
            
        processed_solutions.append(solution)
    return processed_solutions

def main():
    # Create debug directory if it doesn't exist
    script_dir = Path(__file__).parent
    debug_dir = script_dir / "debug_html"
    debug_dir.mkdir(exist_ok=True)
    
    # Read the filtered solutions
    input_file = script_dir / "filtered_solutions.json"
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        solutions = json.load(f)
        
    logger.info(f"Loaded {len(solutions)} solutions from {input_file}")
    
    try:
        # Process all solutions
        updated_solutions = process_solutions_recursive(solutions, debug_dir)
        
        # Save the updated solutions
        output_file = script_dir / "solutions_full_descriptions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_solutions, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved updated solutions to {output_file}")
        
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 