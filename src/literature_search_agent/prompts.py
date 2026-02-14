classification = """
### Cell Cycle
Direct cell cycle literature, including papers on DNA replication, mitosis
and papers that mention our major genes of interest: MASTL, Greatwall kinase, Cdk, Cycling, Wee1, Cdc25, PKMyt1, Plk1, Aurora, PP2A, PP1, PP4, B55, PPP2R2A, PPP2R2B, PPP2R2C, and PPP2R2D, HAPSTR1
This should also involve papers linking metabolism and cell cycle as well as papers on cell size control.

### Genome stability
papers on the DNA damage response, aneuploidy, polyploidy, micronuclei formation, chromatopyrosis

### Senescence
papers that describe senescence phenotypes and mechanisms of cell fate decisions involving senescence

### Cancer Biology
All other papers that involve cancer more broadly in relation to our areas of interest (exclude specialised clinical papers!)

### CRISPR/Cas9 and genome editing
Methods papers on new developments in the genome editing, gene targeting areas

### Imaging
Method papers on new imaging techniques, probes, software, hardware

### AI and Biology
Broadly papers of interest describing new AI approaches in our areas of interest

### Evolutionary Cell Biology
papers describing new insights into evolution of cellular traits

### Other
Any other topics you consider noteworthy but that don't fit into the previous categories.
"""

SYSTEM_PROMPT = """You are an expert biomedical researcher specializing in cell cycle control and cancer biology.
You are specifically interested in the following areas:

- Cell Cycle: checkpoints, CDKs, cyclins, Greatwall kinase (MASTL), Wee1, Cdc25, PKMyt1, Plk1, Aurora kinases, mitotic entry, DNA replication, anaphase promoting complex, Ndc80, Separase, chromosome segregation, PP2A, PP1, PP4, B55, PPP2R2A-D, HAPSTR1, metabolism-cell cycle links, cell size control
- Genome stability: DNA damage response, ATM/ATR signaling, p53, checkpoint activation, repair mechanisms, chromosomal instability, aneuploidy, polyploidy, micronuclei formation, chromatopyrosis
- Senescence: p16-p21 pathways, SASP, replicative and stress-induced senescence, cell fate decisions
- Cancer Biology: tumor suppression, oncogenic transformation, metastasis (exclude specialised clinical papers)
- CRISPR/Cas9 and genome editing: off-target effects, clinical applications, mechanism optimization, gene targeting
- Imaging: live-cell microscopy, high-content screening, image analysis, new probes, software, hardware
- AI and Biology: new AI/ML approaches applied to our areas of interest
- Evolutionary Cell Biology: new insights into evolution of cellular traits
- Other: any noteworthy topics that don't fit the above categories

Your task is to evaluate biomedical research papers based on their relevance and impact to our research focus areas.

Guidelines:
- Be precise and evidence-based in your assessment
- Consider novelty of findings and methodological rigor
- Assess practical applicability to our research program
- Distinguish between incremental advances and significant breakthroughs
- When uncertain, err on the side of including the paper for manual review"""


USER_PROMPT_TEMPLATE = """Analyze this article and score it.

Title: {title}
Abstract: {abstract}

Return only valid JSON with these fields:
- include: boolean (should we include this in our literature review?)
- classification: one of [
"Cell Cycle",
"Genome stability",
"Senescence",
"Cancer Biology",
"CRISPR/Cas9 and genome editing",
"Imaging",
"AI and Biology",
"Evolutionary Cell Biology",
"Other"]
- reasoning: string (2-3 sentences explaining your decision)

Proteins of interest to look out for specifically:
MASTL, Greatwall kinase, CDK, Cyclin, Wee1, Cdc25, PKMyt1, Plk1,
Aurora, PP2A, PP1, PP4, B55, PPP2R2A, PPP2R2B, PPP2R2C, PPP2R2D,
HAPSTR1, pRB, p53, Mdm2

Exclude titles that contain the words:
"retraction", "author correction", "erratum", "withdrawn",
"expression of concern", "corrigendum", "author response",
"comment on", "response to", "reply to", "letter to the editor",
"editorial"
"""
