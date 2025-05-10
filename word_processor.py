import re
import os
import json
import sqlite3
from typing import List, Callable, Optional

def read_and_extract_words(file_path: str) -> List[str]:
    """Read file and extract unique German words."""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # Updated regex to include German characters
    words = re.findall(r'\b[a-zäöüßA-ZÄÖÜ]+\b', text.lower())
    unique_words = sorted(set(words))
    print(f"Found {len(unique_words)} unique words")
    return unique_words

def get_words_not_in_db(words: List[str], db_path: str, progress_callback: Optional[Callable] = None) -> List[str]:
    """Filter out words that are already in the database."""
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get words not in database
    new_words = []
    total_words = len(words)
    
    for i, word in enumerate(words):
        # Update progress if callback is provided
        if progress_callback and i % 10 == 0:
            progress_callback(i, total_words)
        
        # Check if word exists in the database
        cursor.execute("SELECT 1 FROM word_translations WHERE word = ?", (word,))
        if not cursor.fetchone():
            new_words.append(word)
    
    conn.close()
    print(f"Found {len(new_words)} new words not in the database")
    return new_words

def create_batch_translation_file(
    words: List[str],
    language: str,
    book_name: str,
    output_dir: str,
    model_id: str = "ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BJJAaWzW",
    progress_callback: Optional[Callable] = None
) -> str:
    """
    Create a JSONL file for batch processing.
    
    Args:
        words: List of words to translate
        language: Language code (e.g., 'de')
        book_name: Book identifier
        output_dir: Base directory for output
        model_id: The model ID to use for the API requests
        progress_callback: Optional callback for progress updates
        
    Returns:
        str: Path to the created JSONL file
    """
    # Create output directory structure
    language_dir = os.path.join(output_dir, language)
    book_dir = os.path.join(language_dir, "TheDune")
    os.makedirs(book_dir, exist_ok=True)
    
    # Create batch file path
    output_file = os.path.join(book_dir, f"{book_name}_word_sent.jsonl")
    
    # Total number of words for progress calculation
    total_words = len(words)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, word in enumerate(words):
            # Update progress if callback is provided
            if progress_callback and i % 10 == 0:
                progress_callback(i, total_words)
            
            request = {
                "custom_id": f"{word}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "word info"},
                        {"role": "user", "content": f"de-en? {word}"}
                    ],
                    "max_tokens": 1000
                }
            }
            f.write(json.dumps(request, ensure_ascii=False) + '\n')
    
    return output_file

def process_text_to_batch(
    text_file: str,
    db_file: str,
    language: str,
    book_name: str,
    output_dir: str,
    model_id: str,
    progress_callback: Optional[Callable] = None
) -> tuple:
    """
    Main processing function that handles the entire word processing workflow.
    
    Args:
        text_file: Path to the text file
        db_file: Path to the database file
        language: Language code
        book_name: Book name
        output_dir: Output directory
        model_id: Model ID for translation
        progress_callback: Optional callback for progress updates
        
    Returns:
        tuple: (total_words, new_words_count, output_file_path)
    """
    # Set initial progress
    if progress_callback:
        progress_callback(0, 100)
    
    # Extract words from text file
    words = read_and_extract_words(text_file)
    total_words = len(words)
    
    # Update progress to 10%
    if progress_callback:
        progress_callback(10, 100)
    
    # Filter words not in database with a custom progress callback
    def db_progress_callback(value, max_value):
        # Scale progress from 10% to 70%
        if progress_callback:
            progress = 10 + int((value / max_value) * 60)
            progress_callback(progress, 100)
    
    new_words = get_words_not_in_db(words, db_file, db_progress_callback)
    new_words_count = len(new_words)
    
    # Update progress to 70%
    if progress_callback:
        progress_callback(70, 100)
    
    # Create batch file with a custom progress callback
    def batch_progress_callback(value, max_value):
        # Scale progress from 70% to 100%
        if progress_callback and max_value > 0:
            progress = 70 + int((value / max_value) * 30)
            progress_callback(progress, 100)
    
    output_file = create_batch_translation_file(
        new_words,
        language,
        book_name,
        output_dir,
        model_id,
        batch_progress_callback
    )
    
    # Set final progress
    if progress_callback:
        progress_callback(100, 100)
    
    return total_words, new_words_count, output_file