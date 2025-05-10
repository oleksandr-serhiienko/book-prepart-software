import json
import re
import os
from typing import List, Tuple, Callable, Optional

def read_file(file_path: str) -> str:
    """Read the content of a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_book_content(text: str) -> List[Tuple[int, int, str]]:
    """Parse book content into a list of (chapter, sentence_number, text) tuples."""
    current_chapter = 1
    sentence_number = 1
    sentences = []
    
    lines = text.split('\n')
    
    for line in lines:
        if '[CHAPTER MARKER]' in line:
            chapter_match = re.search(r'\[CHAPTER MARKER\] (\d+)', line)
            if chapter_match:
                current_chapter = int(chapter_match.group(1))
                # Reset sentence number at the start of each new chapter
                sentence_number = 1
            continue
            
        if '[BOOK MARKER]' in line:
            continue
            
        # Handle empty lines
        if not line.strip():
            sentences.append((current_chapter, sentence_number, '···'))
        else:
            sentences.append((current_chapter, sentence_number, line.strip()))
            
        sentence_number += 1
    
    return sentences

def create_batch_translation_file(sentences: List[Tuple[int, int, str]], 
                                  language: str, 
                                  book: str,
                                  output_path: str,
                                  model_id: str = "ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BMJ1vRkf",
                                  progress_callback: Optional[Callable] = None) -> str:
    """
    Create a JSONL file for batch processing.
    
    Args:
        sentences: List of (chapter, sentence_num, text) tuples
        language: Language code (e.g., 'de')
        book: Book identifier
        output_path: Path to save the JSONL file
        model_id: The model ID to use for the API requests
        progress_callback: Optional callback for progress updates
        
    Returns:
        str: Path to the created JSONL file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    total_sentences = len(sentences)
    processed = 0
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for chapter, sentence_num, text in sentences:
            request = {
                "custom_id": f"c{chapter}_s{sentence_num}",  # Format: c1_s1 for chapter 1, sentence 1
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
                                    "text": f"de-en |{text}|"
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
            
            # Update progress
            processed += 1
            if processed % 10 == 0 and progress_callback:
                progress_callback(processed, total_sentences)
    
    # Final progress update
    if progress_callback:
        progress_callback(total_sentences, total_sentences)
        
    return output_path

def txt_to_jsonl_batch(input_path: str, 
                       output_path: str, 
                       language: str = "de",
                       model_id: str = "ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BMJ1vRkf",
                       progress_callback: Optional[Callable] = None) -> str:
    """
    Process a text file and create a batch JSONL file for translation.
    
    Args:
        input_path: Path to the input text file
        output_path: Path to save the output JSONL file
        language: Language code (default: 'de')
        model_id: The model ID to use for the API requests
        progress_callback: Optional callback for progress updates
        
    Returns:
        str: Path to the created JSONL file
    """
    try:
        # Read and parse the book
        text = read_file(input_path)
        sentences = parse_book_content(text)
        print(f"Found {len(sentences)} sentences to process")
        
        # Create batch file
        result_path = create_batch_translation_file(
            sentences, 
            language, 
            os.path.splitext(os.path.basename(input_path))[0],
            output_path,
            model_id,
            progress_callback
        )
        
        return result_path
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage when run directly
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert text file to batch JSONL for translation')
    parser.add_argument('input_path', help='Path to input text file')
    parser.add_argument('output_path', help='Path to save the output JSONL file')
    parser.add_argument('--language', default='de', help='Language code (default: de)')
    parser.add_argument('--model', default='ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ', 
                        help='Model ID to use for the API requests')
    
    args = parser.parse_args()
    
    txt_to_jsonl_batch(args.input_path, args.output_path, args.language, args.model)