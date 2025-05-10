import json
import re
import os
from typing import List, Dict, Tuple, Optional, Callable

def parse_translation_response(response: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    """
    Parse the translation response into German and English parts.
    Also return any errors encountered during parsing.
    """
    errors = []
    parts = response.split('|')
    
    if len(parts) != 5:
        errors.append(f"Expected 4 parts in response, but got {len(parts)-1}")
        return None, None, errors
    
    german_parsed = parts[1].strip()
    english_parsed = parts[3].strip()
    return german_parsed, english_parsed, errors

def clean_annotated_text(annotated_text: str) -> str:
    """
    Remove annotations like /14/ from the text.
    E.g., »Aiiih!«/14/ sagte/20/ der/1/ -> »Aiiih!« sagte der
    """
    return re.sub(r'/\d+/', '', annotated_text)

def validate_sentence(
    custom_id: str, 
    response_content: str, 
    original_text: str
) -> Tuple[Optional[str], Optional[str], List[str]]:
    """
    Validate the translation response:
    1. Check if response has exactly 4 parts
    2. Verify if all words in German text have annotations (/number/)
    
    Return the parsed German and English text, along with any errors.
    """
    errors = []
    
    # Parse response
    parts = response_content.split('|')
    if len(parts) != 5:
        errors.append(f"Expected 4 parts in response, but got {len(parts)-1}")
        german_parsed, english_parsed = None, None
    else:
        german_parsed = parts[1].strip()
        english_parsed = parts[3].strip()
        
        # Check if all actual words (containing letters) have annotations
        words = german_parsed.split()
        for word in words:
            if re.search(r'[a-zA-ZäöüßÄÖÜ]', word) and not re.search(r'/\d+/', word):
                errors.append(f"Word '{word}' missing annotation")
    
    return german_parsed, english_parsed, errors

def load_original_texts(file_path: str) -> Dict[str, str]:
    """Load original texts from the requests file."""
    original_texts = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            try:
                request_data = json.loads(line)
                custom_id = request_data.get('custom_id')
                
                # Extract the original text from the user content
                if custom_id and 'body' in request_data and 'messages' in request_data['body']:
                    for message in request_data['body']['messages']:
                        if message.get('role') == 'user' and message.get('content'):
                            content = message['content']
                            if isinstance(content, list):
                                for item in content:
                                    if item.get('type') == 'text' and item.get('text'):
                                        text = item['text']
                                        # Extract the original text between the pipe symbols
                                        if '|' in text:
                                            original_text = text.split('|')[1].strip()
                                            original_texts[custom_id] = original_text
                                            break
            except Exception as e:
                print(f"Error processing request data: {str(e)}")
    
    return original_texts

def process_batch_results(
    results_file_path: str, 
    requests_file_path: str, 
    error_file_path: str,
    progress_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    Process the batch results file, validate sentences, and return only valid sentences.
    Invalid sentences are written to the error file.
    
    Args:
        results_file_path: Path to the results JSONL file
        requests_file_path: Path to the requests JSONL file
        error_file_path: Path to write the error JSONL file
        progress_callback: Optional callback for progress updates
        
    Returns:
        List of dictionaries containing the processed data
    """
    # Load original texts from requests file
    original_texts = load_original_texts(requests_file_path)
    
    # List to store processed data for valid sentences
    processed_data = []
    
    # Count total lines for progress reporting
    with open(results_file_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for line in f if line.strip())
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(error_file_path), exist_ok=True)
    
    # Open error file for writing JSON lines
    with open(error_file_path, 'w', encoding='utf-8') as error_file:
        with open(results_file_path, 'r', encoding='utf-8') as f:
            line_count = 0
            for line in f:
                if not line.strip():
                    continue
                
                line_count += 1
                if line_count % 10 == 0 and progress_callback:
                    progress_callback(line_count, total_lines)
                    
                result = json.loads(line)
                custom_id = result['custom_id']
                # Extract chapter and sentence numbers from custom_id (format: c1_s1)
                chapter_num, sentence_num = map(lambda x: int(x[1:]), custom_id.split('_'))
                original_text = original_texts.get(custom_id)
                
                errors = []
                german_parsed = None
                english_parsed = None
                
                if result.get('error') or result['response']['status_code'] != 200:
                    errors.append("API error or non-200 status code")
                else:
                    try:
                        response_content = result['response']['body']['choices'][0]['message']['content']
                        
                        # Validate the sentence and get parsed results and errors
                        german_parsed, english_parsed, validation_errors = validate_sentence(
                            custom_id, 
                            response_content, 
                            original_text
                        )
                        
                        errors.extend(validation_errors)
                        
                    except Exception as e:
                        errors.append(f"Exception: {str(e)}")
                
                # If there are errors, write them to the error file in JSONL format
                if errors:
                    error_entry = {
                        "custom_id": custom_id,
                        "chapter": chapter_num,
                        "sentence": sentence_num,
                        "original_text": original_text,
                        "response_content": result['response']['body']['choices'][0]['message']['content'] if not result.get('error') and result['response']['status_code'] == 200 else None,
                        "errors": errors
                    }
                    error_file.write(json.dumps(error_entry, ensure_ascii=False) + '\n')
                else:
                    # Only add validated sentences to the processed data
                    processed_data.append({
                        'chapter': chapter_num,
                        'sentence': sentence_num,
                        'original_text': original_text,
                        'german_parsed': german_parsed,
                        'english_parsed': english_parsed
                    })
    
    # Final progress update
    if progress_callback:
        progress_callback(total_lines, total_lines)
        
    return processed_data

def create_sql_inserts(processed_data: List[Dict], output_sql_file: str) -> int:
    """
    Create SQL insert statements from processed data and write to file.
    
    Args:
        processed_data: List of dictionaries containing the processed data
        output_sql_file: Path to write the SQL statements
        
    Returns:
        int: Number of SQL statements written
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_sql_file), exist_ok=True)
    
    sql_inserts = []
    
    for entry in processed_data:
        # Escape single quotes in text fields
        original_text = entry['original_text'].replace("'", "''") if entry['original_text'] else None
        german_parsed = entry['german_parsed'].replace("'", "''") if entry['german_parsed'] else None
        english_parsed = entry['english_parsed'].replace("'", "''") if entry['english_parsed'] else None
        
        # Prepare SQL values
        original_sql = 'NULL' if original_text is None else f"'{original_text}'"
        german_sql = 'NULL' if german_parsed is None else f"'{german_parsed}'"
        english_sql = 'NULL' if english_parsed is None else f"'{english_parsed}'"
        
        sql = f"""INSERT INTO book_sentences 
                (sentence_number, chapter_id, original_text, original_parsed_text, translation_parsed_text)
                VALUES ({entry['sentence']}, {entry['chapter']}, {original_sql}, {german_sql}, {english_sql});"""
        
        sql_inserts.append(sql)
    
    # Write SQL statements to file
    with open(output_sql_file, 'w', encoding='utf-8') as f:
        for sql in sql_inserts:
            f.write(sql + '\n')
    
    return len(sql_inserts)

def create_error_batch_file(
    error_file_path: str, 
    output_batch_path: str, 
    model_id: str = "ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ"
) -> int:
    """
    Create a new batch file for sentences that failed validation.
    This prepares them for reprocessing.
    
    Args:
        error_file_path: Path to the error JSONL file
        output_batch_path: Path to write the new batch file
        model_id: The model ID to use for the API requests
        
    Returns:
        int: Number of error entries processed
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_batch_path), exist_ok=True)
    
    # Read the error file
    errors = []
    with open(error_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                errors.append(json.loads(line))
    
    # Create a new batch file for the errors
    with open(output_batch_path, 'w', encoding='utf-8') as f:
        for error in errors:
            request = {
                "custom_id": f"c{error['chapter']}_s{error['sentence']}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_id,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"de-en |{error['original_text']}|"
                                }
                            ]
                        }
                    ],
                    "response_format": {"type": "text"},
                    "max_tokens": 2048,
                    "temperature": 1,
                    "top_p": 1,
                    "frequency_penalty": 0,
                    "presence_penalty": 0
                }
            }
            f.write(json.dumps(request, ensure_ascii=False) + '\n')
    
    return len(errors)

def get_available_filename(base_path: str) -> str:
    """
    Get an available filename by appending _1, _2, etc. if the file already exists.
    
    Args:
        base_path: Base path for the file
        
    Returns:
        str: Available file path
    """
    if not os.path.exists(base_path):
        return base_path
        
    base_dir = os.path.dirname(base_path)
    base_name, ext = os.path.splitext(os.path.basename(base_path))
    
    counter = 1
    while True:
        new_path = os.path.join(base_dir, f"{base_name}_{counter}{ext}")
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def jsonl_to_db(
    results_file_path: str, 
    db_name: str,
    output_dir: str,
    model_id: str = "ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ",
    progress_callback: Optional[Callable] = None,
    requests_file_path: Optional[str] = None
) -> Tuple[str, str, str, int, int]:
    """
    Process JSONL batch results to create SQL inserts and error file.
    
    Args:
        results_file_path: Path to the results JSONL file
        db_name: Name for the database (used for output file naming)
        output_dir: Directory to save output files
        model_id: The model ID to use for the API requests
        progress_callback: Optional callback for progress updates
        requests_file_path: Optional path to the requests JSONL file
        
    Returns:
        Tuple containing:
        - Path to the SQL insert file
        - Path to the error file
        - Path to the error batch file
        - Number of SQL statements written
        - Number of error entries processed
    """
    # If requests_file_path is not provided, try to infer it from results_file_path
    if requests_file_path is None or not os.path.exists(requests_file_path):
        if requests_file_path is not None and not os.path.exists(requests_file_path):
            print(f"Warning: Provided requests file does not exist: {requests_file_path}")
            
        base_filename = os.path.basename(results_file_path)
        if "_output.jsonl" in base_filename:
            inferred_path = results_file_path.replace("_output.jsonl", "_sent.jsonl")
            if os.path.exists(inferred_path):
                requests_file_path = inferred_path
            else:
                # If inferred path doesn't exist, fall back to results file
                print(f"Warning: Inferred requests file does not exist: {inferred_path}")
                requests_file_path = results_file_path
        else:
            # If not using the standard naming, use the same file
            requests_file_path = results_file_path
            
    # Construct output paths
    base_dir = os.path.join(output_dir, os.path.dirname(results_file_path).split("/")[-1] if "/" in results_file_path else "")
    os.makedirs(base_dir, exist_ok=True)
    
    # Get book name from filename or use the provided db_name
    if "/" in results_file_path:
        book_parts = os.path.basename(results_file_path).split("_")
        book_name = book_parts[0] if len(book_parts) > 0 else db_name
    else:
        book_name = db_name
    
    # Create output file paths
    error_file_path = get_available_filename(os.path.join(base_dir, f"{book_name}_validation_errors.jsonl"))
    sql_file_path = get_available_filename(os.path.join(base_dir, f"{book_name}_sql_inserts.sql"))
    error_batch_path = get_available_filename(os.path.join(base_dir, f"{book_name}_error_batch.jsonl"))
    
    # Process the results
    processed_data = process_batch_results(
        results_file_path, 
        requests_file_path, 
        error_file_path,
        progress_callback
    )
    
    # Create SQL insert statements
    sql_count = create_sql_inserts(processed_data, sql_file_path)
    
    # Create error batch file
    error_count = create_error_batch_file(error_file_path, error_batch_path, model_id)
    
    return sql_file_path, error_file_path, error_batch_path, sql_count, error_count
if __name__ == "__main__":
    # Example usage when run directly
    import argparse
    
    parser = argparse.ArgumentParser(description='Process JSONL batch results to create SQL inserts and error file')
    parser.add_argument('results_file', help='Path to the results JSONL file')
    parser.add_argument('db_name', help='Name for the database (used for output file naming)')
    parser.add_argument('--output-dir', default='output', help='Directory to save output files')
    parser.add_argument('--model', default='ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ', 
                        help='Model ID to use for the API requests')
    
    args = parser.parse_args()
    
    sql_path, error_path, batch_path, sql_count, error_count = jsonl_to_db(
        args.results_file, 
        args.db_name,
        args.output_dir,
        args.model
    )
    
    print(f"Processing complete!")
    print(f"SQL statements ({sql_count}) saved to: {sql_path}")
    print(f"Validation errors ({error_count}) saved to: {error_path}")
    print(f"Error batch file created at: {batch_path}")