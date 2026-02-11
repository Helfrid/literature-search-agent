from datetime import datetime, timedelta
from pathlib import Path

from pubmed import pubmed_search

from literature_search_agent import PUBMED_QUERY

dates = [
    (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
    for i in range(14)
]

for date in dates:
    query = f"{PUBMED_QUERY} AND {date}[dp]"
    pubmed_search(query, date, Path("data"))
