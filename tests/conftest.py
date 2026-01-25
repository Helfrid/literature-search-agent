"""Pytest configuration and fixtures for testing PubMed module."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_pmids():
    """Sample list of PubMed IDs for testing."""
    return ["12345678", "87654321", "11111111"]


@pytest.fixture
def mock_pubmed_search_response():
    """Mock response from Entrez.esearch."""
    return {
        "Count": "3",
        "RetMax": "3",
        "RetStart": "0",
        "IdList": ["12345678", "87654321", "11111111"],
        "WebEnv": "mock_webenv_string",
        "QueryKey": "1",
    }


@pytest.fixture
def mock_pubmed_search_response_empty():
    """Mock empty response from Entrez.esearch."""
    return {
        "Count": "0",
        "RetMax": "0",
        "RetStart": "0",
        "IdList": [],
    }


@pytest.fixture
def mock_pubmed_xml():
    """Mock XML response from Entrez.efetch."""
    xml_content = """<?xml version="1.0"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2019//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd">
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
      <PMID Version="1">12345678</PMID>
      <Article PubModel="Print">
        <Journal>
          <Title>Nature Cell Biology</Title>
        </Journal>
        <ArticleTitle>CRISPR-mediated disruption of CDK4/6 pathways</ArticleTitle>
        <Abstract>
          <AbstractText>We investigated the role of CDK4/6 in cell cycle regulation.</AbstractText>
          <AbstractText>Results showed significant impact on cell proliferation.</AbstractText>
        </Abstract>
        <AuthorList CompleteYN="Y">
          <Author ValidYN="Y">
            <LastName>Smith</LastName>
            <ForeName>John</ForeName>
          </Author>
          <Author ValidYN="Y">
            <LastName>Doe</LastName>
            <ForeName>Jane</ForeName>
          </Author>
        </AuthorList>
      </Article>
      <PubDate>
        <Year>2025</Year>
      </PubDate>
    </MedlineCitation>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
      <PMID Version="1">87654321</PMID>
      <Article PubModel="Print-Electronic">
        <Journal>
          <Title>Cell</Title>
        </Journal>
        <ArticleTitle>Novel approaches to cancer therapy</ArticleTitle>
        <Abstract>
          <AbstractText>This study explores new therapeutic strategies.</AbstractText>
        </Abstract>
        <AuthorList CompleteYN="Y">
          <Author ValidYN="Y">
            <LastName>Johnson</LastName>
            <ForeName>Robert</ForeName>
          </Author>
        </AuthorList>
      </Article>
      <PubDate>
        <Year>2024</Year>
      </PubDate>
    </MedlineCitation>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
      <PMID Version="1">11111111</PMID>
      <Article PubModel="Print">
        <Journal>
          <Title>Science</Title>
        </Journal>
        <ArticleTitle>Molecular mechanisms of autophagy</ArticleTitle>
        <AuthorList CompleteYN="Y">
          <Author ValidYN="Y">
            <LastName>Williams</LastName>
            <ForeName>Sarah</ForeName>
          </Author>
        </AuthorList>
      </Article>
      <PubDate>
        <Year>2024</Year>
      </PubDate>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>"""
    return xml_content


@pytest.fixture
def mock_pubmed_xml_malformed():
    """Mock malformed XML response."""
    return """<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <PMID>99999999</PMID>
    <!-- Missing required fields -->
  </PubmedArticle>
</PubmedArticleSet>"""


@pytest.fixture
def mock_entrez_handle(mock_pubmed_xml):
    """Mock Entrez handle object."""
    handle = MagicMock()
    handle.read.return_value = mock_pubmed_xml
    handle.close.return_value = None
    return handle


@pytest.fixture
def sample_pubmed_articles():
    """Sample PubMedArticle objects for testing."""
    from literature_search_agent.pubmed import PubMedArticle

    return [
        PubMedArticle(
            pmid="12345678",
            title="CRISPR-mediated disruption of CDK4/6 pathways",
            abstract="We investigated the role of CDK4/6 in cell cycle regulation.\nResults showed significant impact on cell proliferation.",
            authors="Smith John; Doe Jane",
            journal="Nature Cell Biology",
            pub_date="2025",
        ),
        PubMedArticle(
            pmid="87654321",
            title="Novel approaches to cancer therapy",
            abstract="This study explores new therapeutic strategies.",
            authors="Johnson Robert",
            journal="Cell",
            pub_date="2024",
        ),
        PubMedArticle(
            pmid="11111111",
            title="Molecular mechanisms of autophagy",
            abstract=None,
            authors="Williams Sarah",
            journal="Science",
            pub_date="2024",
        ),
    ]


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test output files."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir
