#!/usr/bin/env python3
"""
Detailed debug for parsing issues
"""

import os
import sys
import json
import re

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_parse_question_content():
    """Debug the parse_question_content function step by step"""
    print("Debugging parse_question_content")
    print("=" * 50)
    
    # Test content from the actual student answer
    content = "I. 3.5 billion years ago II . ( a ) Sum of all biochemical reactions ( b ) Irascible ( c ) Changes to the machine III . ( a ) Production of diseases resistant plant and animal variables IV . Haden V. ( a ) Paleozoic ( b ) Mesozoic"
    
    print(f"Input content: {content}")
    print()
    
    # Split by roman numerals
    roman_sections = re.split(r'\b(I{1,3}|IV|V|VI{0,3}|IX|X)\s*[\.\)]', content, flags=re.IGNORECASE)
    print(f"Roman sections: {roman_sections}")
    print()
    
    for i in range(1, len(roman_sections), 2):
        if i + 1 < len(roman_sections):
            roman_num = roman_sections[i].lower()
            roman_content = roman_sections[i + 1].strip()
            
            print(f"Roman {roman_num}: '{roman_content}'")
            
            if re.search(r'\([a-z]\)', roman_content):
                print(f"  Has sub-parts")
                
                # Find all sub-parts and their positions
                sub_matches = list(re.finditer(r'\(([a-z])\)', roman_content))
                print(f"  Sub-part matches: {[(m.group(1), m.start(), m.end()) for m in sub_matches]}")
                
                sub_parts = {}
                for idx, match in enumerate(sub_matches):
                    sub_letter = match.group(1).lower()
                    start_pos = match.end()
                    
                    # Find the end position
                    if idx + 1 < len(sub_matches):
                        end_pos = sub_matches[idx + 1].start()
                    else:
                        end_pos = len(roman_content)
                    
                    sub_content = roman_content[start_pos:end_pos].strip()
                    sub_content = re.sub(r'^\s*[\.\)]\s*', '', sub_content)
                    
                    print(f"    Sub-part {sub_letter}: '{sub_content}'")
                    sub_parts[sub_letter] = sub_content
                
                print(f"  Final sub_parts: {sub_parts}")
            else:
                print(f"  No sub-parts, just text: '{roman_content}'")
            print()

def test_improved_parsing():
    """Test an improved parsing approach"""
    print("Testing improved parsing approach")
    print("=" * 50)
    
    content = "I. 3.5 billion years ago II . ( a ) Sum of all biochemical reactions ( b ) Irascible ( c ) Changes to the machine III . ( a ) Production of diseases resistant plant and animal variables IV . Haden V. ( a ) Paleozoic ( b ) Mesozoic"
    
    # More robust approach
    roman_parts = {}
    
    # Split by roman numerals
    roman_sections = re.split(r'\b(I{1,3}|IV|V|VI{0,3}|IX|X)\s*[\.\)]', content, flags=re.IGNORECASE)
    
    for i in range(1, len(roman_sections), 2):
        if i + 1 < len(roman_sections):
            roman_num = roman_sections[i].lower()
            roman_content = roman_sections[i + 1].strip()
            
            print(f"Processing Roman {roman_num}: '{roman_content}'")
            
            # Check for sub-parts
            if re.search(r'\([a-z]\)', roman_content):
                sub_parts = {}
                
                # Use a different approach - split by sub-parts and reconstruct
                parts = re.split(r'\(([a-z])\)', roman_content)
                print(f"  Split parts: {parts}")
                
                for j in range(1, len(parts), 2):
                    if j + 1 < len(parts):
                        sub_letter = parts[j].lower()
                        sub_content = parts[j + 1].strip()
                        
                        # Clean up the content
                        sub_content = re.sub(r'^\s*[\.\)]\s*', '', sub_content)
                        # Remove any remaining sub-part markers
                        sub_content = re.sub(r'\s*\([a-z]\)\s*.*$', '', sub_content)
                        
                        print(f"    Sub-part {sub_letter}: '{sub_content}'")
                        sub_parts[sub_letter] = sub_content
                
                roman_parts[roman_num] = sub_parts
            else:
                # No sub-parts
                roman_content = re.sub(r'^\s*[\.\)]\s*', '', roman_content)
                roman_parts[roman_num] = roman_content.strip()
                print(f"  No sub-parts: '{roman_content}'")
    
    print(f"\nFinal result: {json.dumps(roman_parts, indent=2)}")
    return roman_parts

def main():
    """Run all debug tests"""
    print("GradeMate Parsing Debug Test")
    print("=" * 50)
    
    debug_parse_question_content()
    print("\n" + "=" * 50)
    test_improved_parsing()
    
    print("\n" + "=" * 50)
    print("Debug test completed")
    print("=" * 50)

if __name__ == "__main__":
    main()
