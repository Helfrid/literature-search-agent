from pydantic import BaseModel
from openai import OpenAI
import instructor
from typing import Literal

from literature_search_agent.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class ArticleAnalysis(BaseModel):
    include: bool
    highlight: bool
    classification: Literal["cellcycle", "genome_stability", "cancer_biology", "CRISPR", "imaging", "other"]
    reasoning: str

client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ),
    mode=instructor.Mode.JSON
)

result = client.messages.create(
    model="qwen2.5:7b-instruct-q8_0",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                title="Comprehensive benchmarking single and multi ancestry polygenic score methods with the PGS-hub platform.",
                abstract="Polygenic scores (PGS) quantify genetic contributions to complex traits, yet existing single- and multi-ancestry methods lack multi-dimensional evaluation within a unified framework. Here, we benchmarked 13 state-of-the-art PGS methods across 36 traits in UK Biobank European and African samples. The prediction performance, computational efficiency, the number of variants, and the impact of different linkage disequilibrium (LD) reference sizes were thoroughly assessed for each method. Results of single-ancestry methods demonstrate that LDpred2 has superior performance across a broad spectrum of complex traits in terms of accuracy and computational efficiency; however, other methods remain valuable for specific traits. For multi-ancestry methods, PRS-CSx and X-Wing have comparable performance, whereas LDpred2-multi outperforms both. Notably, we find that increasing the panel size of the LD reference significantly elevates PGS performance for sample sizes below 1,000, and it reaches a plateau when it exceeds 5,000 samples. Furthermore, implementing PGS calculation methods requires considerable technical effort and resource allocation. To support easy use of these PGS methods, we developed a user-friendly online computing platform, PGS-hub, that integrates all evaluated methods and is pre-configured with ancestry-stratified LD panels. This resource enables a scalable and harmonized PGS computation platform for the PGS community.",
            )
        }
    ],
    response_model=ArticleAnalysis,
    temperature=0.3,
    max_tokens=500,
)
print(type(result))
print(result)