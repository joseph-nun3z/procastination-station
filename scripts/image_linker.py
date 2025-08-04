#!/usr/bin/env python3
"""
Image Linker Script for D&D Campaign Wiki

This script finds and copies appropriate images to NPC character pages by:
1. Searching for image files matching character names
2. Copying images into the vault directory structure
3. Updating character pages to include image references
4. Supporting both English and Portuguese versions
"""

import os
import sys
import argparse
from pathlib import Path
import shutil
import re

def find_character_image(character_name, img_base_dir):
    """
    Find image file matching character name in the img directory structure.
    
    Args:
        character_name (str): Name of the character to find image for
        img_base_dir (Path): Base directory containing images
    
    Returns:
        Path: Full path to image file, or None if not found
    """
    # Common image extensions
    extensions = ['.webp', '.png', '.jpg', '.jpeg']
    
    # Search in bestiary/CoS directory first
    cos_bestiary = img_base_dir / 'bestiary' / 'CoS'
    
    if cos_bestiary.exists():
        for ext in extensions:
            # Try exact match
            exact_match = cos_bestiary / f"{character_name}{ext}"
            if exact_match.exists():
                return exact_match
            
            # Try case-insensitive match
            for file in cos_bestiary.iterdir():
                if file.name.lower() == f"{character_name.lower()}{ext}":
                    return file
    
    # Search in bestiary/tokens/CoS directory
    cos_tokens = img_base_dir / 'bestiary' / 'tokens' / 'CoS'
    
    if cos_tokens.exists():
        for ext in extensions:
            # Try exact match
            exact_match = cos_tokens / f"{character_name}{ext}"
            if exact_match.exists():
                return exact_match
            
            # Try case-insensitive match
            for file in cos_tokens.iterdir():
                if file.name.lower() == f"{character_name.lower()}{ext}":
                    return file
    
    # Search in other directories if not found in CoS
    for root, dirs, files in os.walk(img_base_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in extensions and name.lower() == character_name.lower():
                return Path(root) / file
    
    return None

def copy_image_to_vault(source_image_path, vault_dir, character_name):
    """
    Copy image file into the vault directory structure.
    
    Args:
        source_image_path (Path): Source image file path
        vault_dir (Path): Vault directory
        character_name (str): Character name for organizing
    
    Returns:
        str: Relative path to copied image within vault, or None if failed
    """
    # Create assets directory structure
    assets_dir = vault_dir / 'assets' / 'images' / 'characters'
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate safe filename
    safe_name = re.sub(r'[^\w\s-]', '', character_name).strip()
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    
    # Determine destination filename
    dest_filename = f"{safe_name}{source_image_path.suffix}"
    dest_path = assets_dir / dest_filename
    
    try:
        # Copy the image
        shutil.copy2(source_image_path, dest_path)
        print(f"Copied image: {source_image_path} -> {dest_path}")
        
        # Return vault-relative path
        return f"assets/images/characters/{dest_filename}"
    
    except Exception as e:
        print(f"Error copying image {source_image_path}: {e}")
        return None

def update_character_page_with_image(file_path, image_path, character_name):
    """
    Update a character page to include image reference.
    
    Args:
        file_path (Path): Path to the character markdown file
        image_path (str): Relative path to the image file
        character_name (str): Name of the character for alt text
    """
    if not file_path.exists():
        print(f"Warning: Character file not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if image is already present
    if '![' in content and image_path in content:
        print(f"Image already present in {file_path}")
        return False
    
    # Find the position to insert image (after the main title)
    lines = content.split('\n')
    insert_pos = 1  # Default after first line (title)
    
    # Look for basic information section to insert before it
    for i, line in enumerate(lines):
        if line.strip().startswith('## Basic Information') or line.strip().startswith('## Informações Básicas'):
            insert_pos = i
            break
    
    # Create image markdown
    image_markdown = f"\n![{character_name}]({image_path})\n"
    
    # Insert image
    lines.insert(insert_pos, image_markdown)
    
    # Write back to file
    updated_content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Added image to {file_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Link images to NPC character pages')
    parser.add_argument('--vault-dir', type=str, default='/home/jnunez/Projects/DnD/Vaults/curse-of-strahd',
                       help='Path to campaign vault directory')
    parser.add_argument('--img-dir', type=str, default='/home/jnunez/Projects/DnD/Vaults/img',
                       help='Path to images directory')
    parser.add_argument('--character', type=str, 
                       help='Specific character name to process (leave empty to process all)')
    parser.add_argument('--language', choices=['EN', 'PT', 'both'], default='both',
                       help='Language version to update')
    parser.add_argument('--exclude', nargs='*', default=['Strahd von Zarovich', 'Doru', 'Gertruda'],
                       help='Character names to exclude from processing')
    
    args = parser.parse_args()
    
    vault_dir = Path(args.vault_dir)
    img_dir = Path(args.img_dir)
    
    if not vault_dir.exists():
        print(f"Error: Vault directory not found: {vault_dir}")
        return 1
    
    if not img_dir.exists():
        print(f"Error: Image directory not found: {img_dir}")
        return 1
    
    # Character directories
    en_npc_dir = vault_dir / 'EN' / 'Characters' / 'NPCs'
    pt_npc_dir = vault_dir / 'PT' / 'Characters' / 'NPCs'
    
    # Get list of characters to process
    characters_to_process = []
    
    if args.character:
        characters_to_process = [args.character]
    else:
        # Get all characters from EN directory
        if en_npc_dir.exists():
            for file in en_npc_dir.iterdir():
                if file.suffix == '.md':
                    char_name = file.stem
                    if char_name not in args.exclude:
                        characters_to_process.append(char_name)
    
    processed_count = 0
    
    for character_name in characters_to_process:
        print(f"\\nProcessing character: {character_name}")
        
        # Find image for this character
        source_image_path = find_character_image(character_name, img_dir)
        
        if not source_image_path:
            print(f"No image found for {character_name}")
            continue
        
        print(f"Found image: {source_image_path}")
        
        # Copy image to vault
        vault_image_path = copy_image_to_vault(source_image_path, vault_dir, character_name)
        
        if not vault_image_path:
            print(f"Failed to copy image for {character_name}")
            continue
        
        # Update English version
        if args.language in ['EN', 'both']:
            en_file = en_npc_dir / f"{character_name}.md"
            if update_character_page_with_image(en_file, vault_image_path, character_name):
                processed_count += 1
        
        # Update Portuguese version
        if args.language in ['PT', 'both']:
            pt_file = pt_npc_dir / f"{character_name}.md"
            if update_character_page_with_image(pt_file, vault_image_path, character_name):
                processed_count += 1
    
    print(f"\\nProcessed {processed_count} character page updates")
    return 0

if __name__ == '__main__':
    sys.exit(main())