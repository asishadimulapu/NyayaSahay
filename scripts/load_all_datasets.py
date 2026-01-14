# Indian Law RAG Chatbot - Extended Dataset Loader
"""
Load multiple Indian law datasets for comprehensive coverage.
Includes IPC sections, Constitution, and legal Q&A datasets.
"""

import re
import sys
from pathlib import Path
from typing import List
import logging

from datasets import load_dataset
from langchain_core.documents import Document

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_legal_references(text: str) -> dict:
    """Extract act and section info from text."""
    metadata = {"act_name": "Indian Law", "section": None, "title": None}
    
    act_patterns = [
        (r"(Indian Penal Code|IPC)", "Indian Penal Code"),
        (r"(Code of Criminal Procedure|CrPC)", "CrPC"),
        (r"(Constitution of India)", "Constitution of India"),
        (r"(Indian Contract Act)", "Indian Contract Act"),
        (r"(Indian Evidence Act)", "Indian Evidence Act"),
        (r"(Consumer Protection Act)", "Consumer Protection Act"),
        (r"(Motor Vehicles Act)", "Motor Vehicles Act"),
        (r"(Information Technology Act|IT Act)", "IT Act"),
    ]
    
    for pattern, act_name in act_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            metadata["act_name"] = act_name
            break
    
    section_match = re.search(r"Section\s+(\d+[A-Z]?)", text, re.IGNORECASE)
    article_match = re.search(r"Article\s+(\d+[A-Z]?)", text, re.IGNORECASE)
    
    if section_match:
        metadata["section"] = f"Section {section_match.group(1)}"
    elif article_match:
        metadata["section"] = f"Article {article_match.group(1)}"
    
    return metadata


def load_viber1_dataset() -> List[Document]:
    """Load viber1/indian-law-dataset (Q&A format)."""
    logger.info("Loading viber1/indian-law-dataset...")
    documents = []
    
    try:
        dataset = load_dataset("viber1/indian-law-dataset")
        data = dataset["train"]
        
        for idx, row in enumerate(data):
            response = clean_text(row.get("Response", "") or "")
            instruction = clean_text(row.get("Instruction", "") or "")
            
            if len(response) < 50:
                continue
            
            content = f"Question: {instruction}\n\nAnswer: {response}"
            metadata = extract_legal_references(response)
            metadata["source"] = "viber1/indian-law-dataset"
            metadata["index"] = idx
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        logger.info(f"Loaded {len(documents)} from viber1/indian-law-dataset")
    except Exception as e:
        logger.warning(f"Failed to load viber1 dataset: {e}")
    
    return documents


def load_ipc_dataset() -> List[Document]:
    """Load harshitv804/Indian_Penal_Code dataset."""
    logger.info("Loading harshitv804/Indian_Penal_Code...")
    documents = []
    
    try:
        dataset = load_dataset("harshitv804/Indian_Penal_Code")
        data = dataset["train"] if "train" in dataset else list(dataset.values())[0]
        
        for idx, row in enumerate(data):
            # Try different column names
            content = ""
            for field in ["text", "content", "section_text", "description"]:
                if field in row and row[field]:
                    content = clean_text(str(row[field]))
                    break
            
            if not content or len(content) < 30:
                continue
            
            metadata = extract_legal_references(content)
            metadata["act_name"] = "Indian Penal Code"
            metadata["source"] = "harshitv804/Indian_Penal_Code"
            metadata["index"] = idx
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        logger.info(f"Loaded {len(documents)} from IPC dataset")
    except Exception as e:
        logger.warning(f"Failed to load IPC dataset: {e}")
    
    return documents


def load_legal_finetuning_dataset() -> List[Document]:
    """Load Techmaestro369/indian-legal-texts-finetuning."""
    logger.info("Loading Techmaestro369/indian-legal-texts-finetuning...")
    documents = []
    
    try:
        dataset = load_dataset("Techmaestro369/indian-legal-texts-finetuning")
        data = dataset["train"] if "train" in dataset else list(dataset.values())[0]
        
        for idx, row in enumerate(data):
            # This dataset has Q&A pairs
            question = row.get("question", row.get("input", ""))
            answer = row.get("answer", row.get("output", ""))
            
            if question and answer:
                content = f"Question: {clean_text(question)}\n\nAnswer: {clean_text(answer)}"
            else:
                content = clean_text(str(row.get("text", "")))
            
            if len(content) < 50:
                continue
            
            metadata = extract_legal_references(content)
            metadata["source"] = "Techmaestro369/indian-legal-texts-finetuning"
            metadata["index"] = idx
            
            documents.append(Document(page_content=content, metadata=metadata))
        
        logger.info(f"Loaded {len(documents)} from legal finetuning dataset")
    except Exception as e:
        logger.warning(f"Failed to load finetuning dataset: {e}")
    
    return documents


def get_ipc_core_sections() -> List[Document]:
    """Add core IPC sections that are commonly asked about."""
    logger.info("Adding core IPC sections...")
    
    ipc_sections = [
        {
            "section": "Section 302",
            "title": "Punishment for murder",
            "content": "Section 302 of the Indian Penal Code provides the punishment for murder. Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. Murder is defined under Section 300 as culpable homicide with the intention of causing death or with the intention of causing such bodily injury as the offender knows to be likely to cause death, or with the intention of causing bodily injury sufficient in the ordinary course of nature to cause death."
        },
        {
            "section": "Section 300",
            "title": "Murder",
            "content": "Section 300 of the Indian Penal Code defines Murder. Culpable homicide is murder if the act by which the death is caused is done with the intention of causing death, or if it is done with the intention of causing such bodily injury as the offender knows to be likely to cause the death of the person to whom the harm is caused, or if it is done with the intention of causing bodily injury to any person and the bodily injury intended to be inflicted is sufficient in the ordinary course of nature to cause death."
        },
        {
            "section": "Section 376",
            "title": "Punishment for rape",
            "content": "Section 376 of the Indian Penal Code deals with the punishment for rape. Whoever commits rape shall be punished with rigorous imprisonment for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine. The punishment may extend to imprisonment for life which shall mean imprisonment for the remainder of that person's natural life, in certain aggravated cases."
        },
        {
            "section": "Section 307",
            "title": "Attempt to murder",
            "content": "Section 307 of the Indian Penal Code deals with attempt to murder. Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine; and if hurt is caused to any person by such act, the offender shall be liable either to imprisonment for life, or to such punishment as is hereinbefore mentioned."
        },
        {
            "section": "Section 304B",
            "title": "Dowry death",
            "content": "Section 304B of the Indian Penal Code deals with dowry death. Where the death of a woman is caused by any burns or bodily injury or occurs otherwise than under normal circumstances within seven years of her marriage and it is shown that soon before her death she was subjected to cruelty or harassment by her husband or any relative of her husband for, or in connection with, any demand for dowry, such death shall be called dowry death, and such husband or relative shall be deemed to have caused her death."
        },
        {
            "section": "Section 354",
            "title": "Assault or criminal force to woman with intent to outrage her modesty",
            "content": "Section 354 of the Indian Penal Code provides punishment for assault or criminal force to woman with intent to outrage her modesty. Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty, shall be punished with imprisonment of either description for a term which shall not be less than one year but which may extend to five years, and shall also be liable to fine."
        },
        {
            "section": "Section 420",
            "title": "Cheating and dishonestly inducing delivery of property",
            "content": "Section 420 of the Indian Penal Code deals with cheating and dishonestly inducing delivery of property. Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine."
        },
        {
            "section": "Section 498A",
            "title": "Husband or relative of husband subjecting woman to cruelty",
            "content": "Section 498A of the Indian Penal Code deals with husband or relative of husband of a woman subjecting her to cruelty. Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine. Cruelty means any wilful conduct which is of such a nature as is likely to drive the woman to commit suicide or to cause grave injury or danger to life, limb or health of the woman."
        },
        {
            "section": "Section 379",
            "title": "Punishment for theft",
            "content": "Section 379 of the Indian Penal Code provides the punishment for theft. Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both. Theft is defined under Section 378 as the dishonest taking of any movable property out of the possession of any person without that person's consent."
        },
        {
            "section": "Section 378",
            "title": "Theft",
            "content": "Section 378 of the Indian Penal Code defines Theft. Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft. The essential elements are: dishonest intention, movable property, possession of another person, absence of consent, and actual moving of the property."
        },
        {
            "section": "Section 323",
            "title": "Punishment for voluntarily causing hurt",
            "content": "Section 323 of the Indian Penal Code provides punishment for voluntarily causing hurt. Whoever, except in the case provided for by section 334, voluntarily causes hurt, shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both."
        },
        {
            "section": "Section 506",
            "title": "Punishment for criminal intimidation",
            "content": "Section 506 of the Indian Penal Code deals with punishment for criminal intimidation. Whoever commits the offence of criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both. If threat be to cause death or grievous hurt, or to cause the destruction of any property by fire, or to cause an offence punishable with death or imprisonment for life, the punishment may extend to seven years."
        }
    ]
    
    documents = []
    for idx, section_data in enumerate(ipc_sections):
        content = f"""IPC {section_data['section']} - {section_data['title']}

{section_data['content']}

Legal Reference: [Indian Penal Code, {section_data['section']}]"""
        
        documents.append(Document(
            page_content=content,
            metadata={
                "act_name": "Indian Penal Code",
                "section": section_data["section"],
                "title": section_data["title"],
                "source": "core_ipc_sections",
                "index": idx
            }
        ))
    
    logger.info(f"Added {len(documents)} core IPC sections")
    return documents


def get_constitution_articles() -> List[Document]:
    """Add key Constitutional articles."""
    logger.info("Adding Constitution articles...")
    
    articles = [
        {
            "article": "Article 14",
            "title": "Equality before law",
            "content": "Article 14 of the Constitution of India guarantees equality before law. The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. This article embodies the principle that all persons are equal before the law and are entitled to equal protection of the law."
        },
        {
            "article": "Article 19",
            "title": "Protection of certain rights regarding freedom of speech, etc.",
            "content": "Article 19 of the Constitution of India guarantees six fundamental freedoms to all citizens: (a) freedom of speech and expression; (b) freedom to assemble peaceably and without arms; (c) freedom to form associations or unions; (d) freedom to move freely throughout the territory of India; (e) freedom to reside and settle in any part of the territory of India; (f) freedom to practice any profession, or to carry on any occupation, trade or business."
        },
        {
            "article": "Article 21",
            "title": "Protection of life and personal liberty",
            "content": "Article 21 of the Constitution of India provides that no person shall be deprived of his life or personal liberty except according to procedure established by law. This is one of the most fundamental rights. The Supreme Court has expanded its scope to include the right to live with dignity, right to livelihood, right to health, right to education, right to shelter, right to privacy, and many other rights."
        },
        {
            "article": "Article 21A",
            "title": "Right to education",
            "content": "Article 21A of the Constitution of India provides that the State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine. This article was inserted by the Constitution (Eighty-sixth Amendment) Act, 2002."
        },
        {
            "article": "Article 32",
            "title": "Remedies for enforcement of rights",
            "content": "Article 32 of the Constitution of India provides the right to move the Supreme Court for the enforcement of fundamental rights. The Supreme Court shall have power to issue directions or orders or writs, including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto and certiorari, for the enforcement of any of the rights conferred by Part III of the Constitution."
        },
        {
            "article": "Article 226",
            "title": "Power of High Courts to issue writs",
            "content": "Article 226 of the Constitution of India gives the High Courts the power to issue writs including habeas corpus, mandamus, prohibition, quo warranto, and certiorari for the enforcement of fundamental rights and for any other purpose. This power is wider than Article 32 as it can be invoked for purposes other than enforcement of fundamental rights."
        }
    ]
    
    documents = []
    for idx, article_data in enumerate(articles):
        content = f"""Constitution of India - {article_data['article']} - {article_data['title']}

{article_data['content']}

Legal Reference: [Constitution of India, {article_data['article']}]"""
        
        documents.append(Document(
            page_content=content,
            metadata={
                "act_name": "Constitution of India",
                "section": article_data["article"],
                "title": article_data["title"],
                "source": "constitution_articles",
                "index": idx
            }
        ))
    
    logger.info(f"Added {len(documents)} Constitution articles")
    return documents


def load_all_datasets() -> List[Document]:
    """Load all available datasets and combine them."""
    logger.info("=" * 60)
    logger.info("Loading All Indian Law Datasets")
    logger.info("=" * 60)
    
    all_documents = []
    
    # 1. Core IPC sections (most important - always include)
    all_documents.extend(get_ipc_core_sections())
    
    # 2. Constitution articles
    all_documents.extend(get_constitution_articles())
    
    # 3. viber1/indian-law-dataset
    all_documents.extend(load_viber1_dataset())
    
    # 4. Try to load additional datasets
    try:
        all_documents.extend(load_ipc_dataset())
    except:
        pass
    
    try:
        all_documents.extend(load_legal_finetuning_dataset())
    except:
        pass
    
    logger.info("=" * 60)
    logger.info(f"Total documents loaded: {len(all_documents)}")
    logger.info("=" * 60)
    
    return all_documents


if __name__ == "__main__":
    docs = load_all_datasets()
    print(f"\nTotal documents: {len(docs)}")
    
    # Show breakdown by source
    sources = {}
    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    
    print("\nDocuments by source:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")
