import asyncio
from playwright.async_api import async_playwright, TimeoutError
import aiohttp
import logging
import os
from datetime import datetime
import json
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create downloads directory if it doesn't exist
DOWNLOAD_DIR = "brochures"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def download_pdf(session, url, filename):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(await response.read())
                logger.info(f"Successfully downloaded: {filename}")
                return True
            else:
                logger.error(f"Failed to download {url}: Status {response.status}")
                return False
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return False

async def wait_for_search_results(page):
    try:
        # Wait for search input to be ready
        await page.wait_for_selector('.search-results__search-input', timeout=10000)
        
        # Wait for any content in the results list
        await page.wait_for_selector('.search-results__search-panel__filters__results-lists', timeout=10000)
        
        # Wait a bit for dynamic content
        await asyncio.sleep(5)
        
        return True
    except TimeoutError:
        logger.error("Timeout waiting for search results")
        return False

async def main():
    url = "https://www.analog.com/en/search.html?resourceTypes=Technical%20Documentation~Solutions%20Bulletin%20%26%20Brochure"
    
    async with async_playwright() as p:
        # Launch browser with stealth mode
        browser = await p.chromium.launch(headless=False)  # Set to False to see what's happening
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url)
            
            # Wait for the page to load
            if not await wait_for_search_results(page):
                return
            
            # Try to find the Resources filter and click it
            try:
                resources_section = await page.wait_for_selector('text=Resources', timeout=5000)
                if resources_section:
                    await resources_section.click()
                    await asyncio.sleep(2)
            except TimeoutError:
                logger.warning("Resources filter not found, continuing without it")
            
            # Get all PDF links
            pdf_links = await page.evaluate('''
                () => {
                    const results = [];
                    // Look for links in various places
                    const selectors = [
                        '.search-results__search-panel__filters__results-lists a',
                        'a[href*=".pdf"]',
                        '.search-results__container a'
                    ];
                    
                    for (const selector of selectors) {
                        const links = Array.from(document.querySelectorAll(selector));
                        for (const link of links) {
                            if (link.href && link.href.toLowerCase().endsWith('.pdf')) {
                                results.push({
                                    url: link.href,
                                    text: link.textContent.trim() || link.href.split('/').pop()
                                });
                            }
                        }
                    }
                    
                    // Remove duplicates
                    return Array.from(new Set(results.map(JSON.stringify))).map(JSON.parse);
                }
            ''')
            
            if not pdf_links:
                logger.error("No PDF links found")
                return
            
            logger.info(f"Found {len(pdf_links)} PDF links")
            
            # Create a session for downloading
            async with aiohttp.ClientSession() as session:
                tasks = []
                for link in pdf_links:
                    # Create a safe filename from the link text
                    safe_filename = "".join(c for c in link['text'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_filename = safe_filename.replace(' ', '_')
                    if not safe_filename.endswith('.pdf'):
                        safe_filename += '.pdf'
                    
                    # Add timestamp to avoid filename conflicts
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_filename = f"{timestamp}_{safe_filename}"
                    
                    tasks.append(download_pdf(session, link['url'], safe_filename))
                
                # Download all PDFs concurrently
                results = await asyncio.gather(*tasks)
                successful = sum(1 for r in results if r)
                logger.info(f"Download complete. Successfully downloaded {successful} out of {len(pdf_links)} PDFs")
                
        except Exception as e:
            logger.error(f"Error during execution: {str(e)}")
        finally:
            # Add a small delay before closing to see the final state
            await asyncio.sleep(2)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 