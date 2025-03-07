#!/usr/bin/env /workspace/tmp_windsurf/venv/bin/python3

import asyncio
import argparse
import sys
import os
from typing import List, Optional
from playwright.async_api import async_playwright
import html5lib
from multiprocessing import Pool
import time
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

async def fetch_page(url: str, context) -> Optional[str]:
    """Asynchronously fetch a webpage's content."""
    page = await context.new_page()
    try:
        logger.info(f"Fetching {url}")
        # Set common headers
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
        })
        
        # Set shorter timeout and wait for specific elements
        await page.goto(url, timeout=15000)  # 15 seconds timeout
        try:
            # Wait for temperature-related elements with a short timeout
            await page.wait_for_selector('text=/°[CF]|temp|temperature/i', timeout=5000)
        except:
            # Continue even if we don't find temperature elements
            pass
        
        # Wait briefly for dynamic content
        await page.wait_for_timeout(2000)
        
        content = await page.content()
        logger.info(f"Successfully fetched {url}")
        return content
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None
    finally:
        await page.close()

def parse_html(html_content: Optional[str]) -> str:
    """Parse HTML content and extract text with hyperlinks in markdown format."""
    if not html_content:
        return ""
    
    try:
        document = html5lib.parse(html_content)
        result = []
        seen_texts = set()  # To avoid duplicates
        
        def should_skip_element(elem) -> bool:
            """Check if the element should be skipped."""
            # Skip script and style tags
            if elem.tag in ['{http://www.w3.org/1999/xhtml}script', 
                          '{http://www.w3.org/1999/xhtml}style']:
                return True
            # Skip empty elements or elements with only whitespace
            if not any(text.strip() for text in elem.itertext()):
                return True
            return False
        
        def process_element(elem, depth=0):
            """Process an element and its children recursively."""
            if should_skip_element(elem):
                return
            
            # Handle text content
            if hasattr(elem, 'text') and elem.text:
                text = elem.text.strip()
                if text and text not in seen_texts:
                    # Check if this is an anchor tag
                    if elem.tag == '{http://www.w3.org/1999/xhtml}a':
                        href = None
                        for attr, value in elem.items():
                            if attr.endswith('href'):
                                href = value
                                break
                        if href and not href.startswith(('#', 'javascript:')):
                            # Format as markdown link
                            link_text = f"[{text}]({href})"
                            result.append("  " * depth + link_text)
                            seen_texts.add(text)
                    else:
                        result.append("  " * depth + text)
                        seen_texts.add(text)
            
            # Process children
            for child in elem:
                process_element(child, depth + 1)
            
            # Handle tail text
            if hasattr(elem, 'tail') and elem.tail:
                tail = elem.tail.strip()
                if tail and tail not in seen_texts:
                    result.append("  " * depth + tail)
                    seen_texts.add(tail)
        
        # Start processing from the body tag
        body = document.find('.//{http://www.w3.org/1999/xhtml}body')
        if body is not None:
            process_element(body)
        else:
            # Fallback to processing the entire document
            process_element(document)
        
        # Filter out common unwanted patterns
        filtered_result = []
        for line in result:
            # Skip lines that are likely to be noise
            if any(pattern in line.lower() for pattern in [
                'var ', 
                'function()', 
                '.js',
                '.css',
                'google-analytics',
                'disqus',
                '{',
                '}'
            ]):
                continue
            filtered_result.append(line)
        
        return '\n'.join(filtered_result)
    except Exception as e:
        logger.error(f"Error parsing HTML: {str(e)}")
        return ""

async def process_urls(urls: List[str], max_concurrent: int = 5) -> List[str]:
    """Process multiple URLs concurrently."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=['--disable-http2']  # Disable HTTP/2 to avoid protocol errors
        )
        try:
            # Create browser contexts with specific viewport and permissions
            n_contexts = min(len(urls), max_concurrent)
            contexts = []
            for _ in range(n_contexts):
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    permissions=['geolocation']  # Some weather sites need this
                )
                # Add rate limiting delay between context creation
                await asyncio.sleep(0.5)
                contexts.append(context)
            
            # Create tasks for each URL with rate limiting
            tasks = []
            for i, url in enumerate(urls):
                context = contexts[i % len(contexts)]
                # Add delay between requests to avoid rate limiting
                await asyncio.sleep(1)
                task = fetch_page(url, context)
                tasks.append(task)
            
            # Gather results with timeout
            try:
                html_contents = await asyncio.wait_for(
                    asyncio.gather(*tasks),
                    timeout=45  # 45 seconds total timeout
                )
            except asyncio.TimeoutError:
                logger.error("Timeout while fetching pages")
                html_contents = [None] * len(urls)
            
            # Parse HTML contents in parallel
            with Pool() as pool:
                results = pool.map(parse_html, html_contents)
                
            return results
            
        finally:
            # Cleanup
            for context in contexts:
                await context.close()
            await browser.close()

def validate_url(url: str) -> bool:
    """Validate if the given string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description='Fetch and extract text content from webpages.')
    parser.add_argument('urls', nargs='+', help='URLs to process')
    parser.add_argument('--max-concurrent', type=int, default=5,
                       help='Maximum number of concurrent browser instances (default: 5)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Validate URLs
    valid_urls = []
    for url in args.urls:
        if validate_url(url):
            valid_urls.append(url)
        else:
            logger.error(f"Invalid URL: {url}")
    
    if not valid_urls:
        logger.error("No valid URLs provided")
        sys.exit(1)
    
    start_time = time.time()
    try:
        results = asyncio.run(process_urls(valid_urls, args.max_concurrent))
        
        # Print results to stdout
        for url, text in zip(valid_urls, results):
            print(f"\n=== Content from {url} ===")
            print(text)
            print("=" * 80)
        
        logger.info(f"Total processing time: {time.time() - start_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 