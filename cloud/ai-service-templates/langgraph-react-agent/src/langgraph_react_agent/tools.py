import numpy as np
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import MarkdownifyTransformer

web_search = DuckDuckGoSearchResults(output_format="list")

@tool(parse_docstring=True)
def get_arxiv_contents(url: str) -> str:
    """
    Retrieves the content of an arXiv research paper

    Args:
        url: The URL to an arXiv research paper, must be in format 'https://arxiv.org/html/2501.12948v1'

    Returns:
        Full contents of an arXiv research paper
    """
    if "html" in url:
        loader = AsyncHtmlLoader(url)
        md = MarkdownifyTransformer()

        html_content = loader.load()

        if (html_content):
            converted_content = md.transform_documents(html_content)

            return converted_content[0].page_content[:999999]
        else :
            return 'Content not available'
    else:
        return "The URL to an arXiv research paper, must be in format 'https://arxiv.org/html/2501.12948v1'"



