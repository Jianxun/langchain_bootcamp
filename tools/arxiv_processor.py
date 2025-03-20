import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging
from pathlib import Path
import random
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArxivProcessor:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.data = []
        self.categories = defaultdict(int)
        self.years = defaultdict(int)
        
    def analyze_metadata(self, n=1000):
        """Analyze the first n entries of the metadata file"""
        categories = defaultdict(int)
        years = defaultdict(int)
        total_entries = 0
        self.data = []  # Reset data
        
        logging.info(f"Starting analysis of first {n} entries...")
        
        with open(self.input_file, 'r') as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                    
                if i % 10 == 0:  # Report progress every 10 entries
                    logging.info(f"Processing entry {i+1}/{n}...")
                    
                try:
                    entry = json.loads(line)
                    total_entries += 1
                    
                    # Store the entry
                    self.data.append(entry)
                    
                    # Count categories
                    for category in entry.get('categories', '').split():
                        categories[category] += 1
                    
                    # Count years - handle both date formats
                    date_str = entry.get('versions', [{}])[0].get('created', '')
                    try:
                        # Try ISO format first
                        year = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').year
                    except ValueError:
                        try:
                            # Try RFC format
                            year = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z').year
                        except ValueError:
                            logging.warning(f"Could not parse date: {date_str}")
                            continue
                    
                    years[year] += 1
                    
                except json.JSONDecodeError:
                    logging.warning(f"Failed to parse JSON at line {i+1}")
                    continue
                except Exception as e:
                    logging.error(f"Error processing entry at line {i+1}: {str(e)}")
                    continue
        
        logging.info("Analysis complete!")
        return {
            'total_entries': total_entries,
            'categories': Counter(categories),
            'years': Counter(years)
        }
    
    def filter_papers(self, 
                     categories: List[str] = None,
                     min_year: int = None,
                     max_year: int = None,
                     max_papers: int = 1000) -> List[Dict[str, Any]]:
        """Filter papers based on criteria"""
        filtered_papers = []
        
        for paper in self.data:
            # Apply filters
            if categories:
                paper_categories = set(paper.get('categories', '').split())
                if not any(cat in paper_categories for cat in categories):
                    continue
            
            # Filter by year
            try:
                date_str = paper.get('versions', [{}])[0].get('created', '')
                try:
                    # Try ISO format first
                    year = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').year
                except ValueError:
                    try:
                        # Try RFC format
                        year = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z').year
                    except ValueError:
                        logging.warning(f"Could not parse date: {date_str}")
                        continue
                
                if min_year and year < min_year:
                    continue
                if max_year and year > max_year:
                    continue
            except Exception as e:
                logging.error(f"Error processing date: {str(e)}")
                continue
            
            filtered_papers.append(paper)
            
            if len(filtered_papers) >= max_papers:
                break
        
        return filtered_papers
    
    def create_sample_dataset(self, 
                            categories: List[str] = None,
                            min_year: int = None,
                            max_year: int = None,
                            max_papers_per_category: int = 100) -> List[Dict[str, Any]]:
        """Create a balanced sample dataset"""
        # Filter papers
        filtered_papers = self.filter_papers(
            categories=categories,
            min_year=min_year,
            max_year=max_year,
            max_papers=len(self.data)
        )
        
        # Group papers by primary category
        papers_by_category = defaultdict(list)
        for paper in filtered_papers:
            primary_category = paper.get('categories', '').split()[0]
            papers_by_category[primary_category].append(paper)
        
        # Sample papers from each category
        sampled_papers = []
        for category, papers in papers_by_category.items():
            if len(papers) > max_papers_per_category:
                sampled_papers.extend(random.sample(papers, max_papers_per_category))
            else:
                sampled_papers.extend(papers)
        
        return sampled_papers

def main():
    # Initialize processor
    processor = ArxivProcessor('arxiv-metadata-oai-snapshot.json')
    
    # Analyze metadata
    analysis = processor.analyze_metadata(n=10000)
    logger.info("Analysis Results:")
    logger.info(f"Total entries analyzed: {analysis['total_entries']}")
    logger.info("\nTop categories:")
    for cat, count in sorted(analysis['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"{cat}: {count}")
    logger.info("\nPapers by year:")
    for year, count in sorted(analysis['years'].items()):
        logger.info(f"{year}: {count}")
    
    # Create sample dataset
    # Example: Get recent ML papers
    processor.create_sample_dataset(
        categories=['cs.LG', 'cs.AI', 'cs.CL'],  # Machine Learning, AI, and NLP
        min_year=2023,
        max_papers_per_category=100
    )

if __name__ == "__main__":
    main() 