from typing import Optional, List, Dict, Any
from langchain.tools import Tool
from tavily import TavilyClient
from config import config


class SearchTools:
    """LangChain tools for web search using Tavily API"""
    
    def __init__(self):
        """Initialize search tools with Tavily client"""
        if not config.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY not found in configuration")
        
        self.client = TavilyClient(api_key=config.TAVILY_API_KEY)
    
    def search_web(self, query: str) -> str:
        """
        Search the web using Tavily API.
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results as string
        """
        try:
            # Perform search with Tavily
            response = self.client.search(
                query=query,
                search_depth="advanced",  # Use advanced search for better results
                max_results=5
            )
            
            if not response or "results" not in response:
                return f"No results found for query: {query}"
            
            results = response["results"]
            
            if not results:
                return f"No results found for query: {query}"
            
            # Format results
            output = f"Search results for '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "No content available")
                
                # Truncate content if too long
                if len(content) > 300:
                    content = content[:300] + "..."
                
                output += f"{i}. {title}\n"
                output += f"   URL: {url}\n"
                output += f"   {content}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error performing search: {str(e)}"
    
    def search_github(self, query: str) -> str:
        """
        Search GitHub for repositories and projects.
        
        Args:
            query: Search query
            
        Returns:
            Formatted GitHub search results
        """
        try:
            # Add GitHub domain filter
            github_query = f"{query} site:github.com"
            
            response = self.client.search(
                query=github_query,
                search_depth="advanced",
                max_results=5
            )
            
            if not response or "results" not in response:
                return f"No GitHub results found for: {query}"
            
            results = response["results"]
            
            if not results:
                return f"No GitHub results found for: {query}"
            
            output = f"GitHub search results for '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "No description available")
                
                # Truncate content
                if len(content) > 200:
                    content = content[:200] + "..."
                
                output += f"{i}. {title}\n"
                output += f"   Repository: {url}\n"
                output += f"   {content}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching GitHub: {str(e)}"
    
    def search_arxiv(self, query: str) -> str:
        """
        Search arXiv for academic papers.
        
        Args:
            query: Search query
            
        Returns:
            Formatted arXiv search results
        """
        try:
            # Add arXiv domain filter
            arxiv_query = f"{query} site:arxiv.org"
            
            response = self.client.search(
                query=arxiv_query,
                search_depth="advanced",
                max_results=5
            )
            
            if not response or "results" not in response:
                return f"No arXiv papers found for: {query}"
            
            results = response["results"]
            
            if not results:
                return f"No arXiv papers found for: {query}"
            
            output = f"arXiv search results for '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "No abstract available")
                
                # Truncate abstract
                if len(content) > 250:
                    content = content[:250] + "..."
                
                output += f"{i}. {title}\n"
                output += f"   Paper: {url}\n"
                output += f"   Abstract: {content}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching arXiv: {str(e)}"
    
    def search_news(self, query: str) -> str:
        """
        Search for recent news articles.
        
        Args:
            query: Search query
            
        Returns:
            Formatted news search results
        """
        try:
            # Use Tavily's topic parameter for news
            response = self.client.search(
                query=query,
                topic="news",
                search_depth="advanced",
                max_results=5,
                days=7  # Recent news from last 7 days
            )
            
            if not response or "results" not in response:
                return f"No recent news found for: {query}"
            
            results = response["results"]
            
            if not results:
                return f"No recent news found for: {query}"
            
            output = f"Recent news for '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "No content available")
                
                # Truncate content
                if len(content) > 250:
                    content = content[:250] + "..."
                
                output += f"{i}. {title}\n"
                output += f"   Source: {url}\n"
                output += f"   {content}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching news: {str(e)}"
    
    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for search operations.
        
        Returns:
            List of LangChain Tool objects
        """
        return [
            Tool(
                name="search_web",
                func=self.search_web,
                description=(
                    "Search the web for information using Tavily. "
                    "⚠️ ONLY use when user explicitly asks to search, research, find, or investigate a specific topic. "
                    "DO NOT use for unclear inputs, single words/numbers without context, or general questions. "
                    "Input should be a clear, descriptive search query string. "
                    "Returns top search results with titles, URLs, and content snippets."
                )
            ),
            Tool(
                name="search_github",
                func=self.search_github,
                description=(
                    "Search GitHub for repositories, projects, and code. "
                    "⚠️ ONLY use when user explicitly asks to search GitHub or find open-source projects. "
                    "Input should be a search query (e.g., 'langchain python', 'vector database'). "
                    "Returns GitHub repositories with descriptions."
                )
            ),
            Tool(
                name="search_arxiv",
                func=self.search_arxiv,
                description=(
                    "Search arXiv for academic papers and research. "
                    "⚠️ ONLY use when user explicitly asks for papers, research, or academic publications. "
                    "Input should be a search query related to research topics. "
                    "Returns paper titles, URLs, and abstracts."
                )
            ),
            Tool(
                name="search_news",
                func=self.search_news,
                description=(
                    "Search for recent news articles (last 7 days). "
                    "⚠️ ONLY use when user explicitly asks for news, latest updates, or current events. "
                    "Input should be a search query for news topics. "
                    "Returns recent news articles with titles and summaries."
                )
            ),
        ]


def create_search_tools() -> List[Tool]:
    """
    Convenience function to create search tools.
    
    Returns:
        List of LangChain Tool objects for search operations
    """
    search_tools = SearchTools()
    return search_tools.get_tools()
