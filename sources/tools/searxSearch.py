import requests
from bs4 import BeautifulSoup
import os
from sources.tools.tools import Tools  # Import the Tools class

class searxSearch(Tools):
    def __init__(self, base_url: str = None):
        """
        A tool for searching a SearxNG instance and extracting URLs and titles.
        """
        super().__init__()
        self.tag = "searx_search"
        self.base_url = base_url or os.getenv("SEARXNG_BASE_URL")  # Requires a SearxNG base URL
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        if not self.base_url:
            raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")

    def execute(self, blocks: list, safety: bool = True) -> str:
        """Executes a search query against a SearxNG instance using POST and extracts URLs and titles."""
        if not blocks:
            return "Error: No search query provided."

        query = blocks[0].strip()
        if not query:
            return "Error: Empty search query provided."

        search_url = f"{self.base_url}/search"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        data = f"q={query}&categories=general&language=auto&time_range=&safesearch=0&theme=simple"
        try:
            response = requests.post(search_url, headers=headers, data=data, verify=False)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            for article in soup.find_all('article', class_='result'):
                url_header = article.find('a', class_='url_header')
                if url_header:
                    url = url_header['href']
                    title = article.find('h3').text.strip() if article.find('h3') else "No Title"
                    description = article.find('p', class_='content').text.strip() if article.find('p', class_='content') else "No Description"
                    results.append(f"{title} | {url} | {description}")
            return "\n".join(results)  # Return results as a single string, separated by newlines
        except requests.exceptions.RequestException as e:
            return f"Error during search: {e}"

    def execution_failure_check(self, output: str) -> bool:
        """
        Checks if the execution failed based on the output.
        """
        return "Error" in output
