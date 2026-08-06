from __future__ import annotations

from typing import Any

import pandas as pd


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """TODO(student): tao bo evaluation set tu cleaned dataframe.

    Pseudo-code:
    1. Kiem tra so luong document toi thieu.
    2. Chon mot so paper dai dien.
    3. Tao nhieu loai cau hoi:
       - summary
       - authors
       - date
       - categories
    4. Moi row can co:
       - id
       - question_type
       - question
       - ground_truth
       - ground_truth_doc_ids
    5. Ghi file JSON vao output_path.
    """
    import json
    import pathlib


    questions = [
        {
            "id": "q_author_1",
            "question_type": "factual",
            "question": "Who are the authors of the paper titled 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation'?",
            "ground_truth": "The authors of the paper are: Qianwen Cao, Chiyu Zhang, Junxiong Ning, Gongru Li.",
            "ground_truth_doc_ids": ["10.2118/234689-pa"]
        },
        {
            "id": "q_author_2",
            "question_type": "factual",
            "question": "Who are the authors of the paper titled 'Hi‐RAG: A Hierarchical Retrieval‐Augmented Generation Framework for Scalable and Generalisable Tool Selection in Large Language Model Agents'?",
            "ground_truth": "The authors of the paper are: Wei Tian, Yuhao Zhou.",
            "ground_truth_doc_ids": ["10.1111/exsy.70341"]
        },
        {
            "id": "q_author_3",
            "question_type": "factual",
            "question": "Who are the authors of the paper titled 'JADE-Plus: A Multimodal Agentic Retrieval-Augmented Generation Large Language Framework for Diagnostic Support in Jawbone Lesions: Development and Technical Validation Study'?",
            "ground_truth": "The authors of the paper are: Soroush Baseri Saadi, Jonas Ver Berne, Rocharles Cavalcante Fontenele, Peter Claes, Reinhilde Jacobs.",
            "ground_truth_doc_ids": ["10.1007/s10278-026-02086-9"]
        },
        {
            "id": "q_author_4",
            "question_type": "factual",
            "question": "Who are the authors of the paper titled 'Retrieval-Augmented Large-Language-Model-Based Time-Series Forecasting for Cross-Market Equity Analysis'?",
            "ground_truth": "The authors of the paper are: Novanto Yudistira, Yanuar Putra Kharisma Adhiyasa.",
            "ground_truth_doc_ids": ["10.21203/rs.3.rs-10178277/v1"]
        },
        {
            "id": "q_author_5",
            "question_type": "factual",
            "question": "Who are the authors of the paper titled 'Does retrieval-augmented generation impact medical students’ perceptions of large language models? (Preprint)'?",
            "ground_truth": "The authors of the paper are: Rohin Athavale, Alexander Cresswell, Alice Huffman.",
            "ground_truth_doc_ids": ["10.2196/preprints.106157"]
        },
        {
            "id": "q_date_6",
            "question_type": "factual",
            "question": "When was the paper 'An Agentic AI System for Roof Design Compliance Using Computer Vision, Retrieval-Augmented Generation and Large Language Models' published?",
            "ground_truth": "The paper was published on 2026-07-02.",
            "ground_truth_doc_ids": ["10.3390/buildings16132637"]
        },
        {
            "id": "q_date_7",
            "question_type": "factual",
            "question": "When was the paper 'Microsoft Azure artificial intelligence / machine learning hackathon for development of retrieval-augmented generation large language model' published?",
            "ground_truth": "The paper was published on 2026-07-01.",
            "ground_truth_doc_ids": ["10.21079/11681/50309"]
        },
        {
            "id": "q_date_8",
            "question_type": "factual",
            "question": "When was the paper 'The Age of Autonomous Agents: A Bibliometric Review of Agentic AI Architectures, Applications, and Emerging Challenges' published?",
            "ground_truth": "The paper was published on 2026-06-30.",
            "ground_truth_doc_ids": ["10.63646/kpqm1958"]
        },
        {
            "id": "q_date_9",
            "question_type": "factual",
            "question": "When was the paper 'Снижение рисков применения LLM (Large Language Model) в сфере экономической безопасности предприятий молочной промышленности на основе подхода RAG (Retrieval-Augmented Generation)' published?",
            "ground_truth": "The paper was published on 2026-06-15.",
            "ground_truth_doc_ids": ["10.47576/2949-1894.2026.7.7.023"]
        },
        {
            "id": "q_date_10",
            "question_type": "factual",
            "question": "When was the paper 'Retrieval-Augmented Generation (RAG), Generative AI, and\nAgentic AI Governance: An Integrated Enterprise Governance\nPrioritization Architecture' published?",
            "ground_truth": "The paper was published on 2026-06-15.",
            "ground_truth_doc_ids": ["10.21203/rs.3.rs-10012178/v1"]
        },
        {
            "id": "q_summary_11",
            "question_type": "factual",
            "question": "Can you provide a summary for the paper titled 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation'?",
            "ground_truth": "In high-risk industrial settings, leveraging large language models (LLMs) for automated accident analysis and generating safety reports has emerged as an efficient workflow. However, this approach is fundamentally constrained by the models’ inherent knowledge limitations, frequently resulting in analyses that lack domain-specific understanding and regulatory alignment.\n                  To tackle this issue, we introduce SafeRAG, a multistage retrieval-augmented framework for safety report generation. Specifically, the framework uses an entity-centric approach that prompts the LLMs to internally generate domain-specific knowledge. Concurrently, it performs a hierarchical retrieval of external regulations relevant to the accident at topic, concept, and context levels. To obtain well-structured reports, we leverage prompt engineering, integrating internal and external knowledge. Furthermore, a domain-expert persona is also assigned to help LLMs analyze accidents from a specific perspective. To evaluate our approach, we construct a data set from 10,818 accident-description/report pairs collected from real-world industry reports. Experiments show that SafeRAG substantially outperforms baseline LLMs on metrics that include bidirectional encoder representations from transformers (BERTScore) and bidirectional auto-regressive transformers (BARTScore), demonstrating the effectiveness of our approach.",
            "ground_truth_doc_ids": ["10.2118/234689-pa"]
        },
        {
            "id": "q_summary_12",
            "question_type": "factual",
            "question": "Can you provide a summary for the paper titled 'JADE-Plus: A Multimodal Agentic Retrieval-Augmented Generation Large Language Framework for Diagnostic Support in Jawbone Lesions: Development and Technical Validation Study'?",
            "ground_truth": "Diagnosing jawbone lesions in oral and maxillofacial radiology remains challenging due to overlapping radiological features and the need for integrated clinical reasoning. This study aimed to develop and validate JADE-Plus, a novel multimodal, agent-controlled retrieval-augmented generation (RAG) framework for diagnostic decision support in jawbone lesion assessment. JADE-Plus was implemented as a cloud-based, tablet-optimized system integrating a vision-language model (VLM) for panoramic radiograph analysis, a knowledge-grounded RAG module, and an agentic verification loop for diagnostic fusion and re-ranking. The system was evaluated using 40 representative jawbone lesion cases and compared with JADE, GPT-5.4, GPT-5.4 VLM, and ORAD. Performance was assessed using Top-1 and Top-3 accuracy, ablation and statistical analyses, intra-model stability, and response time. JADE-Plus achieved the highest diagnostic performance, with a Top-1 accuracy of 90% (36/40; 95% CI 76–97%) and a Top-3 accuracy of 100%, with no missed diagnoses. Cochran’s\n                    Q\n                    test demonstrated significant differences among models for both Top-3 correctness (\n                    Q\n                     = 25.66,\n                    p\n                     < 0.001) and Top-1 correctness (\n                    Q\n                     = 27.55,\n                    p\n                     < 0.001). Post-hoc McNemar tests with the Benjamini–Hochberg correction showed that JADE-Plus significantly outperformed other models, particularly under the stricter Top-1 evaluation. Ablation analysis showed that the agentic verification stage improved Top-1 and Top-3 accuracy by 15 and 8 percentage points, respectively. JADE-Plus achieved the highest reproducibility (mean Jaccard similarity 0.97 ± 0.12) while maintaining a mean response time of 33 ± 1.5 s per case. JADE-Plus demonstrated superior diagnostic accuracy, stability, and reproducibility compared with baseline systems, supporting multimodal agentic RAG frameworks for jawbone lesion diagnosis.",
            "ground_truth_doc_ids": ["10.1007/s10278-026-02086-9"]
        }
    ]
        
    # Write to JSON file
    output_path = pathlib.Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        
    return questions
