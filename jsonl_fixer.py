import json
import re
import os
from typing import Tuple, Dict, List, Callable, Optional

def fix_sequence_numbers(input_path: str, output_path: str, progress_callback: Optional[Callable] = None) -> str:
    """
    Processes a JSONL file containing translations with numbered words, fixes the numbering
    using the s-prefix approach to ensure sequential ordering by position.
    
    Args:
        input_path (str): Path to the input JSONL file
        output_path (str): Path to save the output JSONL file
        progress_callback (callable): Optional callback for progress updates
        
    Returns:
        str: Path to the fixed JSONL file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Count lines for progress reporting
    with open(input_path, 'r', encoding='utf-8') as infile:
        total_lines = sum(1 for _ in infile)
    
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        line_count = 0
        for line in infile:
            line_count += 1
            try:
                # Parse the JSONL entry
                entry = json.loads(line)
                
                # Get the translation content (assistant's message)
                if 'messages' in entry:
                    for i, message in enumerate(entry['messages']):
                        if message['role'] == 'assistant':
                            # Extract the German and English parts
                            content = message['content']
                            
                            # Split by the comma that separates German and English
                            parts = content.split(', |')
                            if len(parts) != 2:
                                print(f"Warning: Line {line_count} doesn't have the expected format")
                                outfile.write(line)
                                continue
                            
                            german_part = parts[0]
                            english_part = '|' + parts[1]
                            
                            # Apply the prefix-based sequential renumbering
                            german_prefixed = add_prefix_to_numbers(german_part)
                            english_prefixed = add_prefix_to_numbers(english_part)
                            
                            fixed_german, fixed_english = sequential_renumbering(german_prefixed, english_prefixed)
                            
                            # Replace the content with the fixed version
                            entry['messages'][i]['content'] = fixed_german + ', ' + fixed_english
                
                # Write the fixed entry to the output file
                outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')
                
                # Update progress
                if line_count % 10 == 0 and progress_callback:
                    progress_callback(line_count, total_lines)
            
            except Exception as e:
                print(f"Error processing line {line_count}: {e}")
                # Write the original line if there was an error
                outfile.write(line)
    
    print(f"Processing complete. Fixed data saved to {output_path}")
    
    # Final progress update
    if progress_callback:
        progress_callback(total_lines, total_lines)
        
    return output_path

def add_prefix_to_numbers(text: str) -> str:
    """
    Add 's-' prefix to all numbers in the text.
    
    Args:
        text (str): Text with numbered words like "word/5/"
        
    Returns:
        str: Text with prefixed numbers like "word/s-5/"
    """
    pattern = r'(\S+)/(\d+)/'
    
    def replace_with_prefix(match):
        word = match.group(1)
        number = match.group(2)
        return f"{word}/s-{number}/"
    
    return re.sub(pattern, replace_with_prefix, text)

def sequential_renumbering(german_text: str, english_text: str) -> Tuple[str, str]:
    """
    Renumber both German and English texts using the s-prefix approach.
    
    Args:
        german_text (str): German text with prefixed numbers
        english_text (str): English text with prefixed numbers
        
    Returns:
        Tuple[str, str]: Fixed German and English texts
    """
    # Extract all word patterns with their positions in German text
    pattern = r'(\S+)/(?:s-)?(\d+)/'
    german_matches = []
    
    for match in re.finditer(pattern, german_text):
        word = match.group(1)
        number = match.group(2)  # Original number without s- prefix
        position = match.start()
        german_matches.append((word, number, position, match.group(0)))
    
    # Sort by position in text
    german_matches.sort(key=lambda x: x[2])
    
    # Process each word in position order
    next_num = 1
    fixed_german = german_text
    fixed_english = english_text
    processed_numbers = set()
    
    for word, old_num, _, original in german_matches:
        prefix_pattern = f"/s-{old_num}/"
        
        # Check if this number has already been processed
        if prefix_pattern in fixed_german:
            # This number hasn't been processed yet
            # Replace all occurrences of this prefixed number in both texts
            fixed_german = fixed_german.replace(prefix_pattern, f"/{next_num}/")
            fixed_english = fixed_english.replace(prefix_pattern, f"/{next_num}/")
            processed_numbers.add(old_num)
            next_num += 1
    
    return fixed_german, fixed_english

def test_specific_case():
    """Test the function with a specific case."""
    german = "|»Aiiih!«/14/ sagte/15/ der/1/ Fremen/2/ neben/3/ ihm/4/ laut/5/. »Sie/6/ benutzen/7/ diese/8/ idiotischen/9/ Schilde/10/!« Er/11/ zischte/12/ verächtlich/13/.|"
    english = "|»Aiiih!«/14/ the/1/ Fremen/2/ next/3/ to/3/ him/4/ said/15/ loudly/5/. »They/6/ use/7/ those/8/ ridiculous/9/ shields/10/!« He/11/ hissed/12/ contemptuously/13/.|"
    
    german_prefixed = add_prefix_to_numbers(german)
    english_prefixed = add_prefix_to_numbers(english)
    
    fixed_german, fixed_english = sequential_renumbering(german_prefixed, english_prefixed)
    
    print("Original German:", german)
    print("Prefixed German:", german_prefixed)
    print("Fixed German:", fixed_german)
    print("Original English:", english)
    print("Prefixed English:", english_prefixed)
    print("Fixed English:", fixed_english)

if __name__ == "__main__":
    # Example usage when run directly
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix sequence numbers in JSONL translation files')
    parser.add_argument('input_path', help='Path to input JSONL file')
    parser.add_argument('output_path', help='Path to save the fixed JSONL file')
    parser.add_argument('--test', action='store_true', help='Run test case')
    
    args = parser.parse_args()
    
    if args.test:
        test_specific_case()
    else:
        fix_sequence_numbers(args.input_path, args.output_path)