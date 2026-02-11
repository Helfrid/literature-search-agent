import json
import random
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from Bio import Entrez
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from literature_search_agent import PUBMED_QUERY
from literature_search_agent.config import get_logger

logger = get_logger(__name__)

# REQUIRED
Entrez.email = "hh65@sussex.ac.uk"

# OPTIONAL BUT HIGHLY RECOMMENDED
Entrez.api_key = "a221cc0b82b78655e98f3e7f29bf6415b608"


class PubMedArticle(BaseModel):  # type: ignore[misc]
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pmid": "12345678",
                "title": "CRISPR-mediated disruption of CDK4/6",
                "abstract": "We investigated...",
                "authors": "Smith J; Doe A",
                "journal": "Nature Cell Biology",
                "pub_date": "2025",
                "date_fetched": "2025-01-24T10:30:00",
                "doi": "10.1038/s41592-025-02345-6",
            }
        }
    )

    pmid: str
    title: str
    abstract: str | None = None
    authors: str
    journal: str
    pub_date: str | None = None
    date_fetched: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    doi: str | None = None


class ScoringSheet(BaseModel):  # type: ignore[misc]
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scorer": "human",
                "pmid": "12345678",
                "title": "CRISPR-mediated disruption of CDK4/6",
                "abstract": "We investigated...",
                "journal": "Nature Cell Biology",
                "score": 0,
            }
        }
    )

    pmid: str
    title: str
    abstract: str | None = None
    journal: str
    score: int = Field(default=0)


def _pubmed_search(
    query: str, batch_size: int = 1000, max_pmids: int | None = None
) -> list[str]:
    """Search PubMed for articles matching the query.

    Args:
        query: The query to search for.
        batch_size: The number of articles to fetch per batch.

    Returns:
        A list of PubMed IDs.

    Raises:
        RuntimeError: If the search fails or returns no results.
    """
    debug_start_message = f"Searching PubMed for: {query}"
    logger.debug(debug_start_message)

    try:
        handle = Entrez.esearch(
            db="pubmed", term=query, usehistory="y", retmax=0, timeout=30
        )
        record = Entrez.read(handle)
        handle.close()
    except (RuntimeError, ValueError) as e:
        search_error = f"PubMed search failed: {e}"
        logger.error(search_error)
        raise RuntimeError(search_error) from e

    # Check for required keys
    if "Count" not in record:
        raise RuntimeError("PubMed response missing 'Count' field")

    count = int(record["Count"])

    if count == 0:
        no_results_message = f"No results found for query: {query}"
        logger.error(no_results_message)
        raise RuntimeError(no_results_message)

    # Check for WebEnv and QueryKey (needed for batch retrieval)
    if "WebEnv" not in record or "QueryKey" not in record:
        missing_keys_message = "PubMed response missing WebEnv or QueryKey"
        logger.error(missing_keys_message)
        raise RuntimeError(missing_keys_message)

    webenv = record["WebEnv"]
    query_key = record["QueryKey"]

    pmids = []
    target_count = count
    if max_pmids is not None:
        target_count = min(count, max_pmids)
        logger.info("Limiting PMID retrieval to %s results", target_count)

    for start in range(0, target_count, batch_size):
        retmax = min(batch_size, target_count - start)
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                webenv=webenv,
                query_key=query_key,
                retstart=start,
                retmax=retmax,
            )
            batch = Entrez.read(handle)
            handle.close()

            if "IdList" not in batch:
                missing_id_list_message = (
                    f"Warning: batch starting at {start} has no IdList"
                )
                logger.warning(missing_id_list_message)
                continue

            pmids.extend(batch["IdList"])

        except (RuntimeError, ValueError) as e:
            fetch_error = f"Error fetching batch starting at {start}: {e}"
            logger.error(fetch_error)
            continue

        time.sleep(0.34)  # be polite to NCBI

    if not pmids:
        no_pmids_message = f"No PMIDs retrieved despite {count} results found"
        logger.error(no_pmids_message)
        raise RuntimeError(no_pmids_message)

    success_message = f"Successfully retrieved {len(pmids)} PMIDs"
    logger.info(success_message)
    return pmids


def _fetch_pubmed_xml(
    pmids: list[str], batch_size: int = 200
) -> list[PubMedArticle]:
    """Fetch PubMed XML data for a list of PMIDs.

    Args:
        pmids: List of PubMed article IDs to fetch.
        batch_size: Number of PMIDs to fetch per batch.

    Returns:
        List of PubMedArticle Pydantic models.
    """
    all_records = []

    for start in range(0, len(pmids), batch_size):
        batch_pmids = pmids[start : start + batch_size]
        try:
            handle = Entrez.efetch(
                db="pubmed",
                id=",".join(batch_pmids),
                retmode="xml",  # converts list of PMIDs to comma-separated string
                timeout=30,
            )
            xml_data = handle.read()
            handle.close()
        except (RuntimeError, ValueError) as e:
            xml_fetch_error = (
                f"Error fetching XML for batch starting at {start}: {e}"
            )
            logger.warning(xml_fetch_error)
            continue

        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            xml_parse_error = (
                f"Error parsing XML for batch starting at {start}: {e}"
            )
            logger.warning(xml_parse_error)
            continue
        for article in root.findall(".//PubmedArticle"):
            try:
                pmid = article.findtext(".//PMID")
                title = article.findtext(".//ArticleTitle")
                journal = article.findtext(".//Journal/Title")
                pub_date = article.findtext(".//PubDate/Year")

                # Skip articles missing required fields
                if not pmid or not title or not journal:
                    missing_fields_message = f"Skipping article with missing required fields: pmid={pmid}, title={title}, journal={journal}"
                    logger.warning(missing_fields_message)
                    continue

                # Get authors
                authors = article.findall(".//Author")
                authors_str = "; ".join(
                    [
                        " ".join(
                            filter(
                                None,
                                [
                                    a.findtext("LastName"),
                                    a.findtext("ForeName"),
                                ],
                            )
                        )
                        for a in authors
                    ]
                )
                # Get abstract
                abstract_texts = article.findall(".//Abstract/AbstractText")
                abstract = "\n".join(
                    [t.text for t in abstract_texts if t.text]
                )

                # Create Pydantic object (validates automatically)
                pubmed_article = PubMedArticle(
                    pmid=pmid,
                    title=title,
                    journal=journal,
                    pub_date=pub_date,
                    authors=authors_str,
                    abstract=abstract,
                )
                all_records.append(pubmed_article)

            except ValidationError as e:
                validation_error = f"Validation error for PMID {pmid}: {e}"
                logger.warning(validation_error)
                continue
            except (AttributeError, TypeError, ValueError) as e:
                parse_error = f"Error parsing article for PMID {pmid}: {e}"
                logger.warning(parse_error)
                continue
            except Exception as e:  # noqa: BLE001
                unexpected_error = (
                    f"Unexpected error parsing article for PMID {pmid}: {e}"
                )
                logger.warning(unexpected_error)
                continue
        time.sleep(0.34)  # respect NCBI limits
    return all_records


def _save_pubmed_data(
    formatted_records: list[PubMedArticle], date: str, path: Path
) -> None:
    """Save PubMed data to a JSON file.

    Args:
        formatted_records: List of PubMedArticle objects.
        date: Date of the PubMed articles.
        path: Path to the directory to save the JSON file.

    Raises:
        RuntimeError: If saving fails.
    """
    # Sanitize date for filename
    safe_date = date.replace("/", "-").replace("[", "_").replace("]", "")
    filepath = path / f"papers_raw_{safe_date}.json"

    # Create directory if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)
    try:
        with open(filepath, "w") as f:
            json.dump(
                [article.model_dump() for article in formatted_records],
                f,
                indent=2,
            )
        save_success_message = f"Successfully saved {len(formatted_records)} articles to {filepath}"
        logger.info(save_success_message)
    except (OSError, TypeError) as e:
        save_error = f"Error saving articles to {filepath}: {e}"
        logger.error(save_error)
        raise RuntimeError(save_error) from e


def _save_scoring_sheet(
    articles: list[PubMedArticle], date: str, path: Path
) -> None:
    """Save the scoring sheet to a JSON file.

    Args:
        articles: List of PubMedArticle objects.
        date: The date for the filename.
        path: The path to save the scoring sheet.

    Raises:
        RuntimeError: If saving fails.
    """
    # Sanitize date for filename
    safe_date = date.replace("/", "-").replace("[", "_").replace("]", "")
    filepath = path / f"papers_for_manual_{safe_date}.json"

    # Create directory if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)

    # Convert PubMedArticles to ScoringSheets (minimal info only)
    scoring_sheets = [
        ScoringSheet(
            pmid=article.pmid,
            title=article.title,
            journal=article.journal,
        )
        for article in articles
    ]

    save_message = f"Saving {len(scoring_sheets)} scoring sheets to {filepath}"
    logger.info(save_message)

    try:
        with open(filepath, "w") as f:
            json.dump(
                [
                    sheet.model_dump(exclude_none=True)
                    for sheet in scoring_sheets
                ],
                f,
                indent=2,
            )
        save_success_message = f"Successfully saved {len(scoring_sheets)} scoring sheets to {filepath}"
        logger.info(save_success_message)

    except (OSError, TypeError) as e:
        save_error = f"Error saving scoring sheets to {filepath}: {e}"
        logger.error(save_error)
        raise RuntimeError(save_error) from e


def pubmed_search(
    query: str,
    date: str,
    path: Path,
    eval_mode: bool = False,
) -> None:
    """Search PubMed for articles matching the query.

    Args:
        query: The query to search for.
        date: The date to search for.
        path: The path to save the data.
        eval_mode: If True, limit results for evaluation.
    """
    start_message = f"Searching PubMed for: {date}"
    logger.info(start_message)
    max_pmids = 50 if eval_mode else None
    pubmed_articles = _pubmed_search(query, max_pmids=max_pmids)
    pubmed_metadata = _fetch_pubmed_xml(pubmed_articles)

    if eval_mode:
        sample_size = min(50, len(pubmed_metadata))
        pubmed_metadata = random.sample(pubmed_metadata, sample_size)
        _save_pubmed_data(pubmed_metadata, date, path)
        _save_scoring_sheet(pubmed_metadata, date, path)


if __name__ == "__main__":
    for i in range(20):
        date = f"2026-01-{i + 1}"
        query = f"{PUBMED_QUERY} AND {date}[dp]"
        pubmed_search(query, date, Path("data"), eval_mode=True)
