import sqlite3
import json
import os

def convert_db_to_jsonl(db_path, output_path, progress_callback=None):
    """
    Convert database book sentences to JSONL training format.
    
    Args:
        db_path (str): Path to the SQLite database
        output_path (str): Path to save the output JSONL file
        progress_callback (callable): Optional callback for progress updates
        
    Returns:
        str: Path to the created JSONL file
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all sentences with their parsed text
    cursor.execute("""
        SELECT sentence_number, chapter_id, original_text, original_parsed_text, translation_parsed_text 
        FROM book_sentences
        ORDER BY chapter_id, sentence_number
    """)
    
    sentences = cursor.fetchall()
    total_sentences = len(sentences)
    processed = 0
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Open output file
    with open(output_path, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            # Skip sentences without parsed text
            if not sentence[3] or not sentence[4]:
                continue
                
            # Create the message format
            entry = {
                "messages": [
                    {"role": "system", "content": "Text translator and connecting words"},
                    {"role": "user", "content": f"de-en |{sentence[2]}|"},
                    {"role": "assistant", "content": f"|{sentence[3]}|, |{sentence[4]}|"}
                ]
            }
            
            # Write as JSON line
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            # Update progress
            processed += 1
            if processed % 10 == 0 and progress_callback:
                progress_callback(processed, total_sentences)
    
    conn.close()
    print(f"Successfully converted database to JSONL at {output_path}")
    
    # Final progress update
    if progress_callback:
        progress_callback(total_sentences, total_sentences)
        
    return output_path

if __name__ == "__main__":
    # Example usage when run directly
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert SQLite database to JSONL format')
    parser.add_argument('db_path', help='Path to SQLite database')
    parser.add_argument('output_path', help='Path to save the output JSONL file')
    
    args = parser.parse_args()
    
    convert_db_to_jsonl(args.db_path, args.output_path)