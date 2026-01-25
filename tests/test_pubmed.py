"""Comprehensive test suite for the pubmed module."""

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from literature_search_agent.pubmed import (
    PubMedArticle,
    ScoringSheet,
    _fetch_pubmed_xml,
    _pubmed_search,
    _save_pubmed_data,
    _save_scoring_sheet,
    pubmed_search,
)

# ============================================================================
# Tests for PubMedArticle Pydantic Model
# ============================================================================


class TestPubMedArticle:
    """Test suite for PubMedArticle Pydantic model."""

    def test_pubmed_article_valid_creation(self):
        """Test creating a valid PubMedArticle."""
        article = PubMedArticle(
            pmid="12345678",
            title="Test Article",
            abstract="This is a test abstract.",
            authors="Smith J; Doe A",
            journal="Nature",
            pub_date="2025",
        )

        assert article.pmid == "12345678"
        assert article.title == "Test Article"
        assert article.abstract == "This is a test abstract."
        assert article.authors == "Smith J; Doe A"
        assert article.journal == "Nature"
        assert article.pub_date == "2025"
        assert article.date_fetched is not None

    def test_pubmed_article_optional_fields(self):
        """Test PubMedArticle with optional fields as None."""
        article = PubMedArticle(
            pmid="12345678",
            title="Test Article",
            abstract=None,
            authors="Smith J",
            journal="Nature",
            pub_date=None,
        )

        assert article.pmid == "12345678"
        assert article.abstract is None
        assert article.pub_date is None

    def test_pubmed_article_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            PubMedArticle(
                pmid="12345678",
                title="Test Article",
                # Missing required fields: authors, journal
            )

    def test_pubmed_article_date_fetched_auto_generated(self):
        """Test that date_fetched is automatically generated."""
        article = PubMedArticle(
            pmid="12345678",
            title="Test Article",
            authors="Smith J",
            journal="Nature",
        )

        assert article.date_fetched is not None
        # Check it's in ISO format (should not raise)
        from datetime import datetime

        datetime.fromisoformat(article.date_fetched)

    def test_pubmed_article_model_dump(self):
        """Test that PubMedArticle can be serialized to dict."""
        article = PubMedArticle(
            pmid="12345678",
            title="Test Article",
            authors="Smith J",
            journal="Nature",
            abstract="Test abstract",
            pub_date="2025",
        )

        article_dict = article.model_dump()
        assert isinstance(article_dict, dict)
        assert article_dict["pmid"] == "12345678"
        assert article_dict["title"] == "Test Article"


# ============================================================================
# Tests for ScoringSheet Pydantic Model
# ============================================================================


class TestScoringSheet:
    """Test suite for ScoringSheet Pydantic model."""

    def test_scoring_sheet_valid_creation(self):
        """Test creating a valid ScoringSheet."""
        sheet = ScoringSheet(
            pmid="12345678",
            title="Test Article",
            score=5,
        )

        assert sheet.pmid == "12345678"
        assert sheet.title == "Test Article"
        assert sheet.score == 5

    def test_scoring_sheet_default_score(self):
        """Test that score defaults to 0."""
        sheet = ScoringSheet(
            pmid="12345678",
            title="Test Article",
        )

        assert sheet.score == 0

    def test_scoring_sheet_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            ScoringSheet(pmid="12345678")  # Missing title

    def test_scoring_sheet_model_dump(self):
        """Test that ScoringSheet can be serialized to dict."""
        sheet = ScoringSheet(
            pmid="12345678",
            title="Test Article",
            score=3,
        )

        sheet_dict = sheet.model_dump()
        assert isinstance(sheet_dict, dict)
        assert sheet_dict["pmid"] == "12345678"
        assert sheet_dict["score"] == 3


# ============================================================================
# Tests for _pubmed_search Function
# ============================================================================


class TestPubMedSearch:
    """Test suite for _pubmed_search function."""

    @patch("literature_search_agent.pubmed.Entrez.esearch")
    @patch("literature_search_agent.pubmed.Entrez.read")
    def test_pubmed_search_success(
        self, mock_read, mock_esearch, mock_pubmed_search_response, mock_pmids
    ):
        """Test successful PubMed search."""
        # Setup mocks
        mock_handle = MagicMock()
        mock_esearch.return_value = mock_handle
        mock_read.return_value = mock_pubmed_search_response

        # Execute
        result = _pubmed_search("test query", batch_size=1000)

        # Verify
        assert result == mock_pmids
        assert mock_esearch.called
        assert mock_read.called
        mock_handle.close.assert_called()

    @patch("literature_search_agent.pubmed.Entrez.esearch")
    @patch("literature_search_agent.pubmed.Entrez.read")
    def test_pubmed_search_no_results(
        self, mock_read, mock_esearch, mock_pubmed_search_response_empty
    ):
        """Test PubMed search with no results."""
        # Setup mocks
        mock_handle = MagicMock()
        mock_esearch.return_value = mock_handle
        mock_read.return_value = mock_pubmed_search_response_empty

        # Execute and verify
        with pytest.raises(RuntimeError, match="No results found"):
            _pubmed_search("test query")

    @patch("literature_search_agent.pubmed.Entrez.esearch")
    @patch("literature_search_agent.pubmed.Entrez.read")
    def test_pubmed_search_missing_count(self, mock_read, mock_esearch):
        """Test PubMed search with missing Count field."""
        # Setup mocks
        mock_handle = MagicMock()
        mock_esearch.return_value = mock_handle
        mock_read.return_value = {}  # Missing Count

        # Execute and verify
        with pytest.raises(RuntimeError, match="missing 'Count' field"):
            _pubmed_search("test query")

    @patch("literature_search_agent.pubmed.Entrez.esearch")
    @patch("literature_search_agent.pubmed.Entrez.read")
    def test_pubmed_search_missing_webenv(self, mock_read, mock_esearch):
        """Test PubMed search with missing WebEnv or QueryKey."""
        # Setup mocks
        mock_handle = MagicMock()
        mock_esearch.return_value = mock_handle
        mock_read.return_value = {
            "Count": "10",
            # Missing WebEnv and QueryKey
        }

        # Execute and verify
        with pytest.raises(RuntimeError, match="missing WebEnv or QueryKey"):
            _pubmed_search("test query")

    @patch("literature_search_agent.pubmed.Entrez.esearch")
    def test_pubmed_search_api_error(self, mock_esearch):
        """Test PubMed search with API error."""
        # Setup mock to raise exception
        mock_esearch.side_effect = RuntimeError("API connection failed")

        # Execute and verify
        with pytest.raises(RuntimeError, match="PubMed search failed"):
            _pubmed_search("test query")


# ============================================================================
# Tests for _fetch_pubmed_xml Function
# ============================================================================


class TestFetchPubMedXML:
    """Test suite for _fetch_pubmed_xml function."""

    @patch("literature_search_agent.pubmed.Entrez.efetch")
    def test_fetch_pubmed_xml_success(
        self, mock_efetch, mock_pmids, mock_pubmed_xml
    ):
        """Test successful XML fetching and parsing."""
        # Setup mock
        mock_handle = MagicMock()
        mock_handle.read.return_value = mock_pubmed_xml.encode()
        mock_efetch.return_value = mock_handle

        # Execute
        with patch("literature_search_agent.pubmed.time.sleep"):
            result = _fetch_pubmed_xml(mock_pmids, batch_size=200)

        # Verify
        assert len(result) == 3
        assert all(isinstance(article, PubMedArticle) for article in result)
        assert result[0].pmid == "12345678"
        assert (
            result[0].title == "CRISPR-mediated disruption of CDK4/6 pathways"
        )
        assert result[1].pmid == "87654321"
        assert result[2].pmid == "11111111"
        mock_handle.close.assert_called()

    @patch("literature_search_agent.pubmed.Entrez.efetch")
    def test_fetch_pubmed_xml_with_abstract(
        self, mock_efetch, mock_pmids, mock_pubmed_xml
    ):
        """Test that abstracts are properly concatenated."""
        # Setup mock
        mock_handle = MagicMock()
        mock_handle.read.return_value = mock_pubmed_xml.encode()
        mock_efetch.return_value = mock_handle

        # Execute
        with patch("literature_search_agent.pubmed.time.sleep"):
            result = _fetch_pubmed_xml(mock_pmids, batch_size=200)

        # Verify abstract concatenation
        assert result[0].abstract is not None
        assert "We investigated" in result[0].abstract
        assert "Results showed" in result[0].abstract

    @patch("literature_search_agent.pubmed.Entrez.efetch")
    def test_fetch_pubmed_xml_no_abstract(
        self, mock_efetch, mock_pmids, mock_pubmed_xml
    ):
        """Test handling of articles without abstracts."""
        # Setup mock
        mock_handle = MagicMock()
        mock_handle.read.return_value = mock_pubmed_xml.encode()
        mock_efetch.return_value = mock_handle

        # Execute
        with patch("literature_search_agent.pubmed.time.sleep"):
            result = _fetch_pubmed_xml(mock_pmids, batch_size=200)

        # Third article has no abstract in the XML
        # It should have an empty string, not None
        assert result[2].abstract == ""

    @patch("literature_search_agent.pubmed.Entrez.efetch")
    def test_fetch_pubmed_xml_malformed(
        self, mock_efetch, mock_pmids, mock_pubmed_xml_malformed
    ):
        """Test handling of malformed XML."""
        # Setup mock
        mock_handle = MagicMock()
        mock_handle.read.return_value = mock_pubmed_xml_malformed.encode()
        mock_efetch.return_value = mock_handle

        # Execute
        with patch("literature_search_agent.pubmed.time.sleep"):
            result = _fetch_pubmed_xml(mock_pmids, batch_size=200)

        # Should skip malformed articles and return empty list
        assert len(result) == 0

    @patch("literature_search_agent.pubmed.Entrez.efetch")
    def test_fetch_pubmed_xml_api_error(self, mock_efetch, mock_pmids):
        """Test handling of API errors during fetch."""
        # Setup mock to raise exception
        mock_efetch.side_effect = RuntimeError("API connection failed")

        # Execute
        with patch("literature_search_agent.pubmed.time.sleep"):
            result = _fetch_pubmed_xml(mock_pmids, batch_size=200)

        # Should return empty list on error
        assert result == []

    @patch("literature_search_agent.pubmed.Entrez.efetch")
    def test_fetch_pubmed_xml_batching(self, mock_efetch, mock_pubmed_xml):
        """Test that batching works correctly."""
        # Create a list of 5 PMIDs with batch_size=2
        pmids = ["1", "2", "3", "4", "5"]

        # Setup mock
        mock_handle = MagicMock()
        mock_handle.read.return_value = mock_pubmed_xml.encode()
        mock_efetch.return_value = mock_handle

        # Execute
        with patch("literature_search_agent.pubmed.time.sleep"):
            _fetch_pubmed_xml(pmids, batch_size=2)

        # Should be called 3 times (2 + 2 + 1)
        assert mock_efetch.call_count == 3


# ============================================================================
# Tests for _save_pubmed_data Function
# ============================================================================


class TestSavePubMedData:
    """Test suite for _save_pubmed_data function."""

    def test_save_pubmed_data_success(
        self, sample_pubmed_articles, temp_output_dir
    ):
        """Test successful saving of PubMed data."""
        date = "2025-01-24"

        # Execute
        _save_pubmed_data(sample_pubmed_articles, date, temp_output_dir)

        # Verify
        expected_file = temp_output_dir / "papers_raw_2025-01-24.json"
        assert expected_file.exists()

        # Load and verify contents
        with open(expected_file) as f:
            data = json.load(f)

        assert len(data) == 3
        assert data[0]["pmid"] == "12345678"
        assert data[1]["pmid"] == "87654321"

    def test_save_pubmed_data_sanitizes_date(
        self, sample_pubmed_articles, temp_output_dir
    ):
        """Test that date is sanitized for filename."""
        date = "2025/01/24[dp]"

        # Execute
        _save_pubmed_data(sample_pubmed_articles, date, temp_output_dir)

        # Verify filename has sanitized date
        expected_file = temp_output_dir / "papers_raw_2025-01-24_dp.json"
        assert expected_file.exists()

    def test_save_pubmed_data_creates_directory(
        self, sample_pubmed_articles, tmp_path
    ):
        """Test that the function creates the directory if it doesn't exist."""
        non_existent_dir = tmp_path / "new_dir" / "nested"
        date = "2025-01-24"

        # Execute
        _save_pubmed_data(sample_pubmed_articles, date, non_existent_dir)

        # Verify
        assert non_existent_dir.exists()
        expected_file = non_existent_dir / "papers_raw_2025-01-24.json"
        assert expected_file.exists()

    def test_save_pubmed_data_empty_list(self, temp_output_dir):
        """Test saving an empty list of articles."""
        date = "2025-01-24"

        # Execute
        _save_pubmed_data([], date, temp_output_dir)

        # Verify
        expected_file = temp_output_dir / "papers_raw_2025-01-24.json"
        assert expected_file.exists()

        with open(expected_file) as f:
            data = json.load(f)

        assert data == []


# ============================================================================
# Tests for _save_scoring_sheet Function
# ============================================================================


class TestSaveScoringSheet:
    """Test suite for _save_scoring_sheet function."""

    def test_save_scoring_sheet_success(
        self, sample_pubmed_articles, temp_output_dir
    ):
        """Test successful saving of scoring sheet."""
        date = "2025-01-24"

        # Execute
        _save_scoring_sheet(sample_pubmed_articles, date, temp_output_dir)

        # Verify
        expected_file = temp_output_dir / "papers_for_manual_2025-01-24.json"
        assert expected_file.exists()

        # Load and verify contents
        with open(expected_file) as f:
            data = json.load(f)

        assert len(data) == 3
        assert data[0]["pmid"] == "12345678"
        assert (
            data[0]["title"] == "CRISPR-mediated disruption of CDK4/6 pathways"
        )
        assert data[0]["score"] == 0
        # Verify that abstract is not included
        assert "abstract" not in data[0]

    def test_save_scoring_sheet_sanitizes_date(
        self, sample_pubmed_articles, temp_output_dir
    ):
        """Test that date is sanitized for filename."""
        date = "2025/01/24[dp]"

        # Execute
        _save_scoring_sheet(sample_pubmed_articles, date, temp_output_dir)

        # Verify filename has sanitized date
        expected_file = (
            temp_output_dir / "papers_for_manual_2025-01-24_dp.json"
        )
        assert expected_file.exists()

    def test_save_scoring_sheet_creates_directory(
        self, sample_pubmed_articles, tmp_path
    ):
        """Test that the function creates the directory if it doesn't exist."""
        non_existent_dir = tmp_path / "new_dir" / "nested"
        date = "2025-01-24"

        # Execute
        _save_scoring_sheet(sample_pubmed_articles, date, non_existent_dir)

        # Verify
        assert non_existent_dir.exists()
        expected_file = non_existent_dir / "papers_for_manual_2025-01-24.json"
        assert expected_file.exists()

    def test_save_scoring_sheet_default_score(
        self, sample_pubmed_articles, temp_output_dir
    ):
        """Test that all scores default to 0."""
        date = "2025-01-24"

        # Execute
        _save_scoring_sheet(sample_pubmed_articles, date, temp_output_dir)

        # Verify
        expected_file = temp_output_dir / "papers_for_manual_2025-01-24.json"
        with open(expected_file) as f:
            data = json.load(f)

        assert all(item["score"] == 0 for item in data)


# ============================================================================
# Tests for pubmed_search Function (Integration)
# ============================================================================


class TestPubMedSearchIntegration:
    """Test suite for pubmed_search integration function."""

    @patch("literature_search_agent.pubmed._pubmed_search")
    @patch("literature_search_agent.pubmed._fetch_pubmed_xml")
    @patch("literature_search_agent.pubmed._save_pubmed_data")
    @patch("literature_search_agent.pubmed._save_scoring_sheet")
    def test_pubmed_search_full_pipeline(
        self,
        mock_save_scoring,
        mock_save_data,
        mock_fetch,
        mock_search,
        mock_pmids,
        sample_pubmed_articles,
        temp_output_dir,
    ):
        """Test the complete pubmed_search pipeline."""
        # Setup mocks
        mock_search.return_value = mock_pmids
        mock_fetch.return_value = sample_pubmed_articles

        query = "test query"
        date = "2025-01-24"

        # Execute
        pubmed_search(query, date, temp_output_dir)

        # Verify all functions were called
        mock_search.assert_called_once_with(query)
        mock_fetch.assert_called_once_with(mock_pmids)
        mock_save_data.assert_called_once_with(
            sample_pubmed_articles, date, temp_output_dir
        )
        mock_save_scoring.assert_called_once_with(
            sample_pubmed_articles, date, temp_output_dir
        )

    @patch("literature_search_agent.pubmed._pubmed_search")
    def test_pubmed_search_propagates_search_error(
        self, mock_search, temp_output_dir
    ):
        """Test that errors from _pubmed_search are propagated."""
        # Setup mock to raise exception
        mock_search.side_effect = RuntimeError("Search failed")

        # Execute and verify
        with pytest.raises(RuntimeError, match="Search failed"):
            pubmed_search("test query", "2025-01-24", temp_output_dir)
