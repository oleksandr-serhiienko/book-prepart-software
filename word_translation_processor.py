import json
import sqlite3
import os
from typing import Dict, List, Tuple, Any, Set, Optional, Callable
import re

def fix_german_chars(text: str) -> str:
    """Fix German characters that might be escaped."""
    replacements = {
        '\\u00e4': 'ä',
        '\\u00f6': 'ö',
        '\\u00fc': 'ü',
        '\\u00df': 'ß',
        '\\u00c4': 'Ä',
        '\\u00d6': 'Ö',
        '\\u00dc': 'Ü'
    }
    for escaped, umlaut in replacements.items():
        text = text.replace(escaped, umlaut)
    return text

def clean_sql_string(text: str) -> str:
    """Clean and properly escape a string for SQL insertion."""
    # Replace single quotes with single escaped quotes (not double escaped)
    return text.replace("'", "''")

def replace_pipes_with_emphasis(text: str) -> str:
    """Replace text wrapped in pipe symbols with HTML emphasis tags."""
    # Use regex to find text between pipe symbols
    pattern = r'\|(.*?)\|'
    return re.sub(pattern, r'<em>\1</em>', text)

def extract_translations_and_contexts(content: Dict[str, Any]) -> Tuple[str, List[Tuple[str, str]]]:
    """Extract translations and context pairs from the new JSON format."""
    translations = []
    contexts = []
    
    # Extract translations and their examples
    if 'translations' in content:
        for trans in content['translations']:
            # Add the translation meaning
            translations.append(trans['meaning'])
            
            # Add the example if present
            if 'example' in trans:
                contexts.append((
                    trans['example']['source'],
                    trans['example']['target']
                ))
    
    return ', '.join(translations), contexts

def process_batch_results(file_path: str, progress_callback: Optional[Callable] = None) -> Tuple[Dict[str, Dict], Set[str]]:
    """Process the batch results file and return structured data and failed word IDs."""
    words_data = {}
    failed_words = set()  # Keep this as a set since we just need the IDs
    
    # Count total lines for progress reporting
    total_lines = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f if _.strip())
    
    # Process the file
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            
            # Update progress every 10 lines
            if progress_callback and i % 10 == 0:
                progress_callback(i, total_lines)
                
            # Parse JSON and handle German characters
            result = json.loads(line)
            word_id = result['custom_id']
            
            # Check for API errors
            if result.get('error') or result['response']['status_code'] != 200:
                failed_words.add(word_id)
                continue
                
            try:
                content = result['response']['body']['choices'][0]['message']['content']
                # Parse the content as JSON
                content_json = json.loads(fix_german_chars(content))
                
                # Extract translations and contexts
                translations, contexts = extract_translations_and_contexts(content_json)
                
                # Check if translations are empty
                if not translations.strip():
                    failed_words.add(word_id)
                    continue
                
                words_data[word_id] = {
                    'translations': translations,
                    'contexts': contexts,
                    'word_info': content_json.get('word_info', {})
                }
            except Exception as e:
                print(f"Error processing content for {word_id}: {str(e)}")
                failed_words.add(word_id)
                continue
    
    # Final progress update
    if progress_callback:
        progress_callback(total_lines, total_lines)
        
    return words_data, failed_words

def create_error_file(failed_words: Set[str], output_path: str, model_id: str) -> bool:
    """Create a file containing the failed words in the proper request format."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the failed words to a new error file in the same format as the batch creation
        with open(output_path, 'w', encoding='utf-8') as error_f:
            for word in failed_words:
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
                error_f.write(json.dumps(request, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        print(f"\nError creating error file: {str(e)}")
        return False

def create_sql_inserts(words_data: Dict[str, Dict], db_path: str) -> Tuple[List[str], List[str], List[str]]:
    """Create SQL insert statements for words, contexts, and word info.
    Uses current max IDs from the database to avoid conflicts."""
    word_inserts = []
    context_inserts = []
    word_info_inserts = []
    
    # Get the current maximum IDs from the database
    try:
        print(f"Trying to connect to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the word_translations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='word_translations'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("Warning: word_translations table does not exist in the database")
            next_word_id = 1
        else:
            # Get max ID from word_translations
            cursor.execute("SELECT MAX(id) FROM word_translations")
            result = cursor.fetchone()
            
            # Print the actual result for debugging
            print(f"MAX(id) query result: {result}")
            
            next_word_id = 1 if result[0] is None else result[0] + 1
        
        conn.close()
        print(f"Starting with word ID: {next_word_id}")
    except Exception as e:
        import traceback
        print(f"Could not get max IDs from database: {str(e)}")
        print("Exception traceback:")
        traceback.print_exc()
        print("Using default starting ID of 1")
        next_word_id = 1
    
    # Create a sequential numeric ID for each word starting from next_word_id
    word_id_map = {word: idx for idx, word in enumerate(sorted(words_data.keys()), next_word_id)}
    
    # Continue with the rest of the function as before
    for word_id, data in words_data.items():
        # Get the sequential ID for this word
        word_num = word_id_map[word_id]
        
        # Clean and escape translations and the word itself
        translations_escaped = clean_sql_string(data['translations'])
        word_escaped = clean_sql_string(word_id)
        
        # Create word insert
        word_inserts.append(
            f"INSERT INTO word_translations (id, translations, word) "
            f"VALUES ({word_num}, '{translations_escaped}', '{word_escaped}');"
        )
        
        # Create context inserts - Apply pipe replacement here
        for ctx_id, (german, english) in enumerate(data['contexts'], 1):
            # Replace pipes with emphasis tags in both German and English texts
            german_with_emphasis = replace_pipes_with_emphasis(german)
            english_with_emphasis = replace_pipes_with_emphasis(english)
            
            # Clean and escape the processed texts
            german_escaped = clean_sql_string(german_with_emphasis)
            english_escaped = clean_sql_string(english_with_emphasis)
            
            context_inserts.append(
                f"INSERT INTO word_contexts (word_id, context_id, original_text, translated_text) "
                f"VALUES ({word_num}, {ctx_id}, '{german_escaped}', '{english_escaped}');"
            )
        
        # Create word info insert
        if data['word_info']:
            word_info_json = clean_sql_string(json.dumps(data['word_info']))
            word_info_inserts.append(
                f"INSERT INTO word_info (word_id, info) "
                f"VALUES ({word_num}, '{word_info_json}');"
            )
    
    return word_inserts, context_inserts, word_info_inserts

def generate_schema() -> str:
    """Generate the SQL schema for word translations tables."""
    return """
CREATE TABLE IF NOT EXISTS word_translations (
    id INTEGER PRIMARY KEY,
    translations TEXT,
    word TEXT                  
);

CREATE TABLE IF NOT EXISTS word_contexts (
    word_id INTEGER,
    context_id INTEGER,
    original_text TEXT,
    translated_text TEXT,
    PRIMARY KEY (word_id, context_id),
    FOREIGN KEY (word_id) REFERENCES word_translations(id)
);

CREATE TABLE IF NOT EXISTS word_info (
    word_id INTEGER PRIMARY KEY,
    info TEXT,
    FOREIGN KEY (word_id) REFERENCES word_translations(id)
);
"""

def process_word_translations(
    input_file: str, 
    output_dir: str,
    book_name: str,
    language: str = "de",
    model_id: str = "ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BJJAaWzW",
    progress_callback: Optional[Callable] = None,
    db_path: Optional[str] = None  # Add parameter for explicit database path
) -> Tuple[str, str, int, int]:
    """
    Process JSONL word translations to SQL inserts.
    
    Args:
        input_file: Path to the JSONL file with word translations
        output_dir: Directory to save the output files
        book_name: Name of the book (used for file naming)
        language: Language code (default: 'de')
        model_id: The model ID to use for the API requests for error batch
        progress_callback: Optional callback for progress updates
        db_path: Optional explicit path to the database to use for ID generation
        
    Returns:
        Tuple containing:
        - Path to the SQL file
        - Path to the error batch file
        - Number of successful word translations
        - Number of failed word translations
    """
    # Create output directory structure
    language_dir = os.path.join(output_dir, language)
    book_dir = os.path.join(language_dir, "TheDune")
    os.makedirs(book_dir, exist_ok=True)
    
    # Define output file paths
    sql_file = os.path.join(book_dir, f"{book_name}_word_translations.sql")
    error_file = os.path.join(book_dir, f"{book_name}_word_error.jsonl")
    
    # Database path for ID retrieval
    if db_path is None:
        # If no explicit db_path is provided, use the default location
        db_path = os.path.join(book_dir, f"{book_name}.db")
    
    print(f"Using database path for ID retrieval: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    # Process the batch results
    words_data, failed_words = process_batch_results(input_file, progress_callback)
    
    # Create error file for failed words
    create_error_file(failed_words, error_file, model_id)
    
    # Create SQL statements
    word_inserts, context_inserts, word_info_inserts = create_sql_inserts(words_data, db_path)
    
    # Write SQL file
    with open(sql_file, 'w', encoding='utf-8') as f:
        # Write schema
        f.write(generate_schema())
        
        # Write inserts
        for insert in word_inserts:
            f.write(insert + '\n')
        for insert in context_inserts:
            f.write(insert + '\n')
        for insert in word_info_inserts:
            f.write(insert + '\n')
    
    return sql_file, error_file, len(words_data), len(failed_words)