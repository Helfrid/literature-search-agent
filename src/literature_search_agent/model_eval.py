import asyncio
from typing import List

from pydantic import BaseModel
from typing import Literal

from literature_search_agent.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class ArticleAnalysis(BaseModel):
    title: str
    abstract: str
    journal: str
    pub_date: str
    doi: str
    include: bool
    highlight: bool
    classification: Literal[
        "Cell Cycle",
        "Genome stability",
        "Senescence",
        "Cancer Biology",
        "CRISPR/Cas9 and genome editing",
        "Imaging",
        "AI and Biology",
        "Evolutionary Cell Biology",
        "Other",
    ]
    reasoning: str

async def score_papers(
    client,
    papers: List[dict],
    model: str = "qwen2.5:7b-instruct-q8_0"
) -> List[ArticleAnalysis | None]:
    """Score multiple papers asynchronously"""
    
    tasks = []
    for paper in papers:
        task = score_single_paper(
            client,
            paper['title'],
            paper['abstract'],
            model
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

async def score_single_paper(
    client,
    title: str,
    abstract: str,
    model: str
) -> ArticleAnalysis | None:
    """Score a single paper"""
    try:
        result = client.messages.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": USER_PROMPT_TEMPLATE.format(
                        title=title,
                        abstract=abstract
                    )
                }
            ],
            response_model=ArticleAnalysis,
            temperature=0.3,
            max_tokens=500,
        )
        return result
    except Exception as e:
        print(f"Error scoring '{title}': {e}")
        return None

# Usage
async def main():
    papers = [
        {
            "title": "Novel mechanisms of p16-mediated senescence",
            "abstract": "This study reveals..."
        },
        {
            "title": "CRISPR-based therapy for cancer",
            "abstract": "We demonstrate..."
        },
        {
            "title": "Deep learning for image analysis",
            "abstract": "We present a new approach..."
        }
    ]
    
    results = await score_papers(client, papers)
    
    for paper, result in zip(papers, results):
        if result:
            print(f"Title: {paper['title']}")
            print(f"Include: {result.include}, Highlight: {result.highlight}")
            print(f"Classification: {result.classification}")
            print(f"Reasoning: {result.reasoning}\n")

# Run it
asyncio.run(main())