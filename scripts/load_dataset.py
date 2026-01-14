# Indian Law RAG Chatbot - Dataset Loader
"""
Load and preprocess the viber1/indian-law-dataset from Hugging Face.
Converts raw data into LangChain Documents with proper metadata.

Viva Explanation:
- Loads dataset using HuggingFace datasets library
- Cleans and normalizes legal text
- Creates structured documents with metadata for citations
- Metadata includes act name, section, and title for proper referencing
"""

import re
import sys
from pathlib import Path
from typing import List, Optional
import logging

from datasets import load_dataset
from langchain_core.documents import Document

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize legal text.
    
    Args:
        text: Raw text from dataset
        
    Returns:
        str: Cleaned text
        
    Viva Explanation:
    - Removes excessive whitespace
    - Normalizes line endings
    - Preserves legal structure (sections, articles)
    """
    if not text:
        return ""
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Fix common OCR issues in legal documents
    text = text.replace('ﬁ', 'fi')
    text = text.replace('ﬂ', 'fl')
    
    return text


def extract_act_info(row: dict) -> dict:
    """
    Extract act name, section, and title from dataset row.
    
    Args:
        row: Dataset row
        
    Returns:
        dict: Extracted metadata
    """
    metadata = {
        "act_name": "Unknown Act",
        "section": None,
        "title": None,
        "source": "viber1/indian-law-dataset"
    }
    
    # Try different field names based on dataset structure
    # The dataset may have varying column names
    
    # Extract act name
    for field in ["Act", "act", "Act_Name", "act_name", "law_name"]:
        if field in row and row[field]:
            metadata["act_name"] = str(row[field]).strip()
            break
    
    # Extract section
    for field in ["Section", "section", "section_number", "article"]:
        if field in row and row[field]:
            section_val = str(row[field]).strip()
            # Format as "Section X" or "Article X"
            if not section_val.lower().startswith(("section", "article")):
                section_val = f"Section {section_val}"
            metadata["section"] = section_val
            break
    
    # Extract title
    for field in ["Title", "title", "section_title", "heading"]:
        if field in row and row[field]:
            metadata["title"] = str(row[field]).strip()
            break
    
    return metadata


def load_indian_law_dataset() -> List[Document]:
    """
    Load the viber1/indian-law-dataset and convert to LangChain Documents.
    
    Returns:
        List[Document]: List of LangChain Document objects
        
    Viva Explanation:
    - Uses HuggingFace datasets library for efficient loading
    - Dataset format: Instruction (question) + Response (answer with legal info)
    - Creates Document objects with page_content and metadata
    """
    logger.info("Loading viber1/indian-law-dataset from Hugging Face...")
    
    try:
        # Load the dataset
        dataset = load_dataset("viber1/indian-law-dataset")
        
        # Get the train split (or first available split)
        if "train" in dataset:
            data = dataset["train"]
        else:
            split_name = list(dataset.keys())[0]
            data = dataset[split_name]
            logger.info(f"Using split: {split_name}")
        
        logger.info(f"Dataset loaded with {len(data)} entries")
        logger.info(f"Columns: {data.column_names}")
        
        # Convert to Documents
        # This dataset has 'Instruction' (question) and 'Response' (answer) columns
        documents = []
        skipped = 0
        
        for idx, row in enumerate(data):
            # Get the Response (contains the legal information)
            response = row.get("Response", "") or ""
            instruction = row.get("Instruction", "") or ""
            
            # Clean the text
            response = clean_text(response)
            instruction = clean_text(instruction)
            
            # Skip if too short
            if len(response) < 50:
                skipped += 1
                continue
            
            # Combine instruction and response for better context
            # Format: "Q: [question] A: [answer with legal info]"
            content = f"Question: {instruction}\n\nAnswer: {response}"
            
            # Try to extract act/section info from the response text
            metadata = extract_legal_references(response)
            metadata["index"] = idx
            metadata["instruction"] = instruction[:200]  # Store first 200 chars of question
            metadata["source"] = "viber1/indian-law-dataset"
            
            # Create Document
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(doc)
            
            # Progress logging
            if (idx + 1) % 5000 == 0:
                logger.info(f"Processed {idx + 1} / {len(data)} entries...")
        
        logger.info(f"Created {len(documents)} documents (skipped {skipped} short entries)")
        
        return documents
    
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        raise


def extract_legal_references(text: str) -> dict:
    """
    Extract legal act names and section numbers from text.
    
    Args:
        text: Legal text content
        
    Returns:
        dict: Extracted metadata
    """
    metadata = {
        "act_name": "Indian Law",
        "section": None,
        "title": None
    }
    
    # Common Indian law patterns
    act_patterns = [
        r"(Indian Penal Code|IPC)",
        r"(Code of Criminal Procedure|CrPC)",
        r"(Code of Civil Procedure|CPC)",
        r"(Constitution of India)",
        r"(Indian Contract Act)",
        r"(Indian Evidence Act)",
        r"(Transfer of Property Act)",
        r"(Hindu Marriage Act)",
        r"(Muslim Personal Law)",
        r"(Companies Act)",
        r"(Income Tax Act)",
        r"(GST Act)",
        r"(Consumer Protection Act)",
        r"(Right to Information Act|RTI)",
        r"(Motor Vehicles Act)",
        r"(Negotiable Instruments Act)",
        r"(Arbitration and Conciliation Act)",
        r"(Information Technology Act|IT Act)",
    ]
    
    # Find act name
    for pattern in act_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["act_name"] = match.group(1)
            break
    
    # Find section/article numbers
    section_match = re.search(r"Section\s+(\d+[A-Z]?)", text, re.IGNORECASE)
    article_match = re.search(r"Article\s+(\d+[A-Z]?)", text, re.IGNORECASE)
    
    if section_match:
        metadata["section"] = f"Section {section_match.group(1)}"
    elif article_match:
        metadata["section"] = f"Article {article_match.group(1)}"
    
    return metadata


def create_sample_documents() -> List[Document]:
    """
    Create sample documents for testing when dataset is unavailable.
    
    Returns:
        List[Document]: Sample Indian law documents
    """
    logger.warning("Creating sample documents for testing...")
    
    sample_data = [
        {
            "content": """Section 302 of the Indian Penal Code deals with Punishment for murder. 
            Whoever commits murder shall be punished with death, or imprisonment for life, 
            and shall also be liable to fine.""",
            "act_name": "Indian Penal Code",
            "section": "Section 302",
            "title": "Punishment for murder"
        },
        {
            "content": """Section 379 of the Indian Penal Code deals with Punishment for theft. 
            Whoever commits theft shall be punished with imprisonment of either description 
            for a term which may extend to three years, or with fine, or with both.""",
            "act_name": "Indian Penal Code",
            "section": "Section 379",
            "title": "Punishment for theft"
        },
        {
            "content": """Article 21 of the Constitution of India provides that no person shall 
            be deprived of his life or personal liberty except according to procedure established 
            by law. This is one of the most fundamental rights guaranteed under Part III of 
            the Constitution.""",
            "act_name": "Constitution of India",
            "section": "Article 21",
            "title": "Protection of life and personal liberty"
        },
        {
            "content": """Article 14 of the Constitution of India guarantees equality before law. 
            The State shall not deny to any person equality before the law or the equal 
            protection of the laws within the territory of India.""",
            "act_name": "Constitution of India",
            "section": "Article 14",
            "title": "Equality before law"
        },
        {
            "content": """Section 420 of the Indian Penal Code deals with Cheating and dishonestly 
            inducing delivery of property. Whoever cheats and thereby dishonestly induces the 
            person deceived to deliver any property to any person, shall be punished with 
            imprisonment of either description for a term which may extend to seven years, 
            and shall also be liable to fine.""",
            "act_name": "Indian Penal Code",
            "section": "Section 420",
            "title": "Cheating and dishonestly inducing delivery of property"
        },
        {
            "content": """Section 304A of the Indian Penal Code deals with causing death by 
            negligence. Whoever causes the death of any person by doing any rash or negligent 
            act not amounting to culpable homicide, shall be punished with imprisonment of 
            either description for a term which may extend to two years, or with fine, or 
            with both.""",
            "act_name": "Indian Penal Code",
            "section": "Section 304A",
            "title": "Causing death by negligence"
        },
        {
            "content": """Article 19 of the Constitution of India guarantees certain freedoms 
            to all citizens including the freedom of speech and expression, freedom to assemble 
            peaceably and without arms, freedom to form associations or unions, freedom to move 
            freely throughout the territory of India, freedom to reside and settle in any part 
            of India, and freedom to practice any profession or to carry on any occupation, 
            trade or business.""",
            "act_name": "Constitution of India",
            "section": "Article 19",
            "title": "Protection of certain rights regarding freedom of speech etc."
        },
        {
            "content": """Section 498A of the Indian Penal Code deals with husband or relative 
            of husband of a woman subjecting her to cruelty. Whoever being the husband or the 
            relative of the husband of a woman, subjects such woman to cruelty shall be punished 
            with imprisonment for a term which may extend to three years and shall also be 
            liable to fine.""",
            "act_name": "Indian Penal Code",
            "section": "Section 498A",
            "title": "Husband or relative of husband subjecting woman to cruelty"
        }
    ]
    
    documents = []
    for idx, data in enumerate(sample_data):
        doc = Document(
            page_content=data["content"],
            metadata={
                "act_name": data["act_name"],
                "section": data["section"],
                "title": data["title"],
                "source": "sample_data",
                "index": idx
            }
        )
        documents.append(doc)
    
    logger.info(f"Created {len(documents)} sample documents")
    return documents


def main():
    """Main function to load and display dataset info."""
    try:
        documents = load_indian_law_dataset()
        
        print("\n" + "=" * 60)
        print("Dataset Loading Summary")
        print("=" * 60)
        print(f"Total documents: {len(documents)}")
        
        if documents:
            print("\nSample document:")
            print(f"  Content: {documents[0].page_content[:200]}...")
            print(f"  Metadata: {documents[0].metadata}")
        
        # Count by act
        act_counts = {}
        for doc in documents:
            act = doc.metadata.get("act_name", "Unknown")
            act_counts[act] = act_counts.get(act, 0) + 1
        
        print("\nDocuments by Act:")
        for act, count in sorted(act_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {act}: {count}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print("\nFalling back to sample documents...")
        documents = create_sample_documents()
        print(f"Created {len(documents)} sample documents")


if __name__ == "__main__":
    main()
