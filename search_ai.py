"""Search AI module - Replacement for missing search_ai package.

This module provides search functionality using DuckDuckGo search
as a replacement for the missing search_ai package.
"""

from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)


class SearchResult:
    """Represents a search result with a link attribute."""
    
    def __init__(self, link: str, title: str = "", body: str = ""):
        """Initialize a search result.
        
        Args:
            link: The URL of the search result
            title: The title of the search result
            body: The body/snippet of the search result
        """
        self.link = link
        self.title = title
        self.body = body
    
    def model_dump(self) -> Dict[str, Any]:
        """Return a dictionary representation of the result.
        
        This method is expected by the privacy_policy_analyzer.py code.
        
        Returns:
            Dictionary containing the result data
        """
        return {
            'link': self.link,
            'title': self.title,
            'body': self.body
        }
    
    def __dict__(self) -> Dict[str, Any]:
        """Return dictionary representation for compatibility."""
        return self.model_dump()


def search(query: str, max_results: int = 5) -> List[SearchResult]:
    """Search for results using DuckDuckGo.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of SearchResult objects
    """
    try:
        logger.info(f"Searching for: {query}")
        
        # Use DuckDuckGo search
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(query, max_results=max_results):
                search_result = SearchResult(
                    link=result.get('href', ''),
                    title=result.get('title', ''),
                    body=result.get('body', '')
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} search results")
            return results
            
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        return []


def search_news(query: str, max_results: int = 5) -> List[SearchResult]:
    """Search for news results using DuckDuckGo.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of SearchResult objects
    """
    try:
        logger.info(f"Searching news for: {query}")
        
        # Use DuckDuckGo news search
        with DDGS() as ddgs:
            results = []
            for result in ddgs.news(query, max_results=max_results):
                search_result = SearchResult(
                    link=result.get('url', ''),
                    title=result.get('title', ''),
                    body=result.get('body', '')
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} news results")
            return results
            
    except Exception as e:
        logger.error(f"Error performing news search: {e}")
        return []


def search_images(query: str, max_results: int = 5) -> List[SearchResult]:
    """Search for image results using DuckDuckGo.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of SearchResult objects
    """
    try:
        logger.info(f"Searching images for: {query}")
        
        # Use DuckDuckGo image search
        with DDGS() as ddgs:
            results = []
            for result in ddgs.images(query, max_results=max_results):
                search_result = SearchResult(
                    link=result.get('image', ''),
                    title=result.get('title', ''),
                    body=result.get('thumbnail', '')
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} image results")
            return results
            
    except Exception as e:
        logger.error(f"Error performing image search: {e}")
        return []
