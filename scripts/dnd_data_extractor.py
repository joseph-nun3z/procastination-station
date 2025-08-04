#!/usr/bin/env python3
"""
D&D 5e Data Extractor for Curse of Strahd Campaign Wiki

This script extracts and formats D&D 5e data from the external 5e-data directory
and creates properly formatted Obsidian markdown files for campaign integration.

Usage:
    python dnd_data_extractor.py --type creature --name "Ismark Kolyanovich"
    python dnd_data_extractor.py --type item --name "Longsword"
    python dnd_data_extractor.py --type spell --name "Magic Missile"
    python dnd_data_extractor.py --type race --name "Human"
    python dnd_data_extractor.py --extract-cos-data  # Extract all CoS-related data
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

class DnDDataExtractor:
    def __init__(self, data_dir: str, vault_dir: str):
        """
        Initialize the data extractor.
        
        Args:
            data_dir: Path to the 5e-data directory
            vault_dir: Path to the campaign vault directory
        """
        self.data_dir = Path(data_dir)
        self.vault_dir = Path(vault_dir)
        self.reference_dir = self.vault_dir / "Shared" / "5e-Reference"
        
        # Ensure reference directory exists
        self.reference_dir.mkdir(parents=True, exist_ok=True)
        
        # Data type mappings
        self.data_sources = {
            'creatures': [
                'bestiary/bestiary-cos.json',
                'bestiary/bestiary-mm.json',
                'bestiary/bestiary-mpmm.json'
            ],
            'items': [
                'items.json',
                'items-base.json'
            ],
            'spells': [
                'spells/spells-phb.json',
                'spells/spells-xge.json',
                'spells/spells-tce.json'
            ],
            'races': [
                'races.json'
            ],
            'adventures': [
                'adventure/adventure-cos.json'
            ],
            'classes': [
                'class/class-fighter.json',
                'class/class-cleric.json',
                'class/class-wizard.json',
                'class/class-rogue.json',
                'class/class-ranger.json',
                'class/class-paladin.json',
                'class/class-barbarian.json',
                'class/class-bard.json',
                'class/class-druid.json',
                'class/class-monk.json',
                'class/class-sorcerer.json',
                'class/class-warlock.json',
                'class/class-artificer.json'
            ]
        }

    def load_json_data(self, file_path: str) -> Optional[Dict]:
        """Load and parse JSON data from file."""
        full_path = self.data_dir / 'data' / file_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: File not found: {full_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {full_path}: {e}")
            return None

    def find_creature(self, name: str) -> Optional[Dict]:
        """Find a creature by name in bestiary files."""
        for source_file in self.data_sources['creatures']:
            data = self.load_json_data(source_file)
            if not data or 'monster' not in data:
                continue
                
            for creature in data['monster']:
                if creature.get('name', '').lower() == name.lower():
                    creature['_source_file'] = source_file
                    return creature
        
        return None

    def find_item(self, name: str) -> Optional[Dict]:
        """Find an item by name in item files."""
        for source_file in self.data_sources['items']:
            data = self.load_json_data(source_file)
            if not data:
                continue
                
            # Handle different JSON structures
            items = data.get('item', data.get('baseitem', []))
            for item in items:
                if item.get('name', '').lower() == name.lower():
                    item['_source_file'] = source_file
                    return item
        
        return None

    def find_spell(self, name: str) -> Optional[Dict]:
        """Find a spell by name in spell files."""
        for source_file in self.data_sources['spells']:
            data = self.load_json_data(source_file)
            if not data or 'spell' not in data:
                continue
                
            for spell in data['spell']:
                if spell.get('name', '').lower() == name.lower():
                    spell['_source_file'] = source_file
                    return spell
        
        return None

    def find_race(self, name: str) -> Optional[Dict]:
        """Find a race by name in race files, prioritizing XPHB over PHB."""
        # Define source priority order (XPHB first, then PHB, then others)
        source_priority = ['XPHB', 'PHB', 'SCAG', 'VGM', 'MPMM', 'XGE', 'TCE']
        
        found_races = []
        
        for source_file in self.data_sources['races']:
            data = self.load_json_data(source_file)
            if not data or 'race' not in data:
                continue
                
            for race in data['race']:
                if race.get('name', '').lower() == name.lower():
                    race['_source_file'] = source_file
                    found_races.append(race)
        
        if not found_races:
            return None
        
        # If only one race found, return it
        if len(found_races) == 1:
            return found_races[0]
        
        # Sort by source priority
        def get_priority(race):
            source = race.get('source', 'ZZZ')  # ZZZ ensures unknown sources go last
            try:
                return source_priority.index(source)
            except ValueError:
                return len(source_priority)  # Unknown sources go to end
        
        sorted_races = sorted(found_races, key=get_priority)
        return sorted_races[0]

    def format_ability_score(self, score: int) -> str:
        """Format ability score with modifier."""
        modifier = (score - 10) // 2
        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        return f"{score} ({modifier_str})"

    def format_creature_stats(self, creature: Dict) -> str:
        """Format creature statistics as markdown."""
        stats = []
        
        # Basic info
        size = creature.get('size', ['Unknown'])
        if isinstance(size, list):
            size_str = size[0] if size else 'Unknown'
        else:
            size_str = size
        stats.append(f"**Size:** {size_str}")
        
        creature_type = creature.get('type', {})
        if isinstance(creature_type, dict):
            type_str = creature_type.get('type', 'Unknown')
        else:
            type_str = creature_type
        stats.append(f"**Type:** {type_str}")
        
        stats.append(f"**Alignment:** {self.format_alignment(creature.get('alignment', []))}")
        
        # Combat stats
        if 'ac' in creature:
            ac_info = creature['ac'][0] if isinstance(creature['ac'], list) else creature['ac']
            ac_str = str(ac_info.get('ac', ac_info)) if isinstance(ac_info, dict) else str(ac_info)
            if isinstance(ac_info, dict) and 'from' in ac_info:
                ac_str += f" ({', '.join(ac_info['from'])})"
            stats.append(f"**AC:** {ac_str}")
        
        if 'hp' in creature:
            hp = creature['hp']
            hp_str = str(hp.get('average', hp)) if isinstance(hp, dict) else str(hp)
            if isinstance(hp, dict) and 'formula' in hp:
                hp_str += f" ({hp['formula']})"
            stats.append(f"**HP:** {hp_str}")
        
        if 'speed' in creature:
            speed = creature['speed']
            if isinstance(speed, dict):
                speed_parts = []
                for move_type, distance in speed.items():
                    if move_type == 'walk':
                        speed_parts.insert(0, f"{distance} ft.")
                    else:
                        speed_parts.append(f"{move_type} {distance} ft.")
                stats.append(f"**Speed:** {', '.join(speed_parts)}")
        
        # Ability scores
        abilities = ['str', 'dex', 'con', 'int', 'wis', 'cha']
        ability_line = " ".join([
            f"**{ability.upper()}:** {self.format_ability_score(creature.get(ability, 10))}"
            for ability in abilities if ability in creature
        ])
        if ability_line:
            stats.append(ability_line)
        
        # Skills, saves, etc.
        if 'skill' in creature:
            skills = ', '.join([f"{skill.title()} {bonus}" for skill, bonus in creature['skill'].items()])
            stats.append(f"**Skills:** {skills}")
        
        if 'save' in creature:
            saves = ', '.join([f"{save.upper()} {bonus}" for save, bonus in creature['save'].items()])
            stats.append(f"**Saving Throws:** {saves}")
        
        if 'resist' in creature:
            stats.append(f"**Damage Resistances:** {', '.join(creature['resist'])}")
        
        if 'immune' in creature:
            stats.append(f"**Damage Immunities:** {', '.join(creature['immune'])}")
        
        if 'conditionImmune' in creature:
            stats.append(f"**Condition Immunities:** {', '.join(creature['conditionImmune'])}")
        
        if 'senses' in creature:
            stats.append(f"**Senses:** {', '.join(creature['senses'])}")
        
        if 'passive' in creature:
            stats.append(f"**Passive Perception:** {creature['passive']}")
        
        if 'languages' in creature:
            stats.append(f"**Languages:** {', '.join(creature['languages'])}")
        
        if 'cr' in creature:
            stats.append(f"**Challenge Rating:** {creature['cr']}")
        
        return '\n'.join(stats)

    def format_alignment(self, alignment: List) -> str:
        """Format alignment array to readable string."""
        if not alignment:
            return "Unknown"
        
        alignment_map = {
            'L': 'Lawful', 'N': 'Neutral', 'C': 'Chaotic',
            'G': 'Good', 'E': 'Evil', 'A': 'Any'
        }
        
        if len(alignment) == 1 and alignment[0] == 'A':
            return "Any alignment"
        
        return ' '.join([alignment_map.get(a, a) for a in alignment])

    def format_actions(self, creature: Dict) -> str:
        """Format creature actions as markdown."""
        actions = []
        
        for action_type in ['action', 'bonus', 'reaction', 'legendary']:
            if action_type in creature:
                actions.append(f"### {action_type.title()} Actions")
                for action in creature[action_type]:
                    name = action.get('name', 'Unknown')
                    entries = action.get('entries', [])
                    action_text = self.format_entries(entries)
                    actions.append(f"**{name}:** {action_text}")
                actions.append("")
        
        return '\n'.join(actions)

    def format_entries(self, entries: List) -> str:
        """Format entry arrays to readable text."""
        if not entries:
            return ""
        
        result = []
        for entry in entries:
            if isinstance(entry, str):
                # Clean up formatting tags
                clean_entry = re.sub(r'\{@[^}]+\}', lambda m: self.clean_formatting_tag(m.group()), entry)
                result.append(clean_entry)
            elif isinstance(entry, dict):
                if entry.get('type') == 'list':
                    items = entry.get('items', [])
                    for item in items:
                        result.append(f"• {item}")
        
        return ' '.join(result)

    def clean_formatting_tag(self, tag: str) -> str:
        """Clean 5etools formatting tags."""
        # Remove the outer braces and split by |
        content = tag[2:-1]  # Remove {@...}
        parts = content.split('|')
        
        # Handle specific tag types
        tag_type = parts[0].split(' ')[0] if parts else ''
        
        if tag_type in ['variantrule', 'rule']:
            # For rules, return just the rule name
            rule_name = ' '.join(parts[0].split(' ')[1:]) if len(parts[0].split(' ')) > 1 else parts[0]
            return rule_name
        elif tag_type == 'filter':
            # For filters, return the filter text
            return ' '.join(parts[0].split(' ')[1:]) if len(parts[0].split(' ')) > 1 else parts[0]
        elif tag_type == 'condition':
            # For conditions, return just the condition name
            condition_name = ' '.join(parts[0].split(' ')[1:]) if len(parts[0].split(' ')) > 1 else parts[0]
            return condition_name
        elif tag_type == 'dice':
            # For dice, return just the dice notation
            dice_notation = ' '.join(parts[0].split(' ')[1:]) if len(parts[0].split(' ')) > 1 else parts[0]
            return dice_notation
        elif tag_type == 'action':
            # For actions, return just the action name
            action_name = ' '.join(parts[0].split(' ')[1:]) if len(parts[0].split(' ')) > 1 else parts[0]
            return action_name
        else:
            # Return the first part (usually the display text)
            return parts[0] if parts else tag

    def create_creature_page(self, creature: Dict, language: str = 'EN') -> str:
        """Create a formatted creature page in markdown."""
        name = creature.get('name', 'Unknown')
        source = creature.get('source', 'Unknown')
        page = creature.get('page', 'Unknown')
        
        # Determine if this is an NPC or monster
        is_npc = creature.get('isNpc', False) or creature.get('isNamedCreature', False)
        
        content = [
            f"# {name}",
            "",
            f"*Source: {source}, p. {page}*",
            "",
            self.format_creature_stats(creature),
            ""
        ]
        
        # Add actions if present
        actions = self.format_actions(creature)
        if actions:
            content.extend(["## Actions", "", actions])
        
        # Add traits if present
        if 'trait' in creature:
            content.extend(["## Special Abilities", ""])
            for trait in creature['trait']:
                name = trait.get('name', 'Unknown')
                entries = self.format_entries(trait.get('entries', []))
                content.append(f"**{name}:** {entries}")
                content.append("")
        
        # Add tags
        tags = ["#5e-reference"]
        if is_npc:
            tags.append("#npc")
        else:
            tags.append("#monster")
        
        if source.lower() == 'cos':
            tags.append("#curse-of-strahd")
        
        content.extend([
            "---",
            f"**Tags:** {' '.join(tags)}",
            f"**Source Data:** `{creature.get('_source_file', 'unknown')}`"
        ])
        
        return '\n'.join(content)

    def create_item_page(self, item: Dict, language: str = 'EN') -> str:
        """Create a formatted item page in markdown."""
        name = item.get('name', 'Unknown')
        
        content = [
            f"# {name}",
            ""
        ]
        
        # Basic properties
        if 'type' in item:
            content.append(f"**Type:** {item['type']}")
        
        if 'rarity' in item:
            content.append(f"**Rarity:** {item['rarity']}")
        
        if 'reqAttune' in item:
            attune = "Yes" if item['reqAttune'] else "No"
            content.append(f"**Requires Attunement:** {attune}")
        
        if 'value' in item:
            content.append(f"**Value:** {item['value']} gp")
        
        if 'weight' in item:
            content.append(f"**Weight:** {item['weight']} lb.")
        
        if 'dmg1' in item:
            damage = item['dmg1']
            content.append(f"**Damage:** {damage}")
        
        if 'dmgType' in item:
            content.append(f"**Damage Type:** {item['dmgType']}")
        
        if 'property' in item:
            properties = ', '.join(item['property'])
            content.append(f"**Properties:** {properties}")
        
        # Description
        if 'entries' in item:
            content.extend(["", "## Description", ""])
            description = self.format_entries(item['entries'])
            content.append(description)
        
        content.extend([
            "",
            "---",
            "**Tags:** #5e-reference #item",
            f"**Source Data:** `{item.get('_source_file', 'unknown')}`"
        ])
        
        return '\n'.join(content)

    def create_race_page(self, race: Dict, language: str = 'EN') -> str:
        """Create a formatted race page in markdown with comprehensive player information."""
        name = race.get('name', 'Unknown')
        source = race.get('source', 'Unknown')
        
        content = [
            f"# {name}",
            ""
        ]
        
        # Basic race properties with XPHB-style formatting
        if 'creatureTypes' in race:
            types = race['creatureTypes']
            if isinstance(types, list):
                content.append(f"**Creature Types:** {', '.join(types)}")
            else:
                content.append(f"**Creature Types:** {types}")
        
        if 'size' in race:
            sizes = race['size']
            if isinstance(sizes, list):
                size_str = ', '.join([str(s) for s in sizes])
                content.append(f"**Size:** {size_str}")
                # Add size description if available
                if 'sizeEntry' in race:
                    size_entry = race['sizeEntry']
                    if isinstance(size_entry, dict) and 'entries' in size_entry:
                        size_desc = self.format_entries(size_entry['entries'])
                        content.append(f"({size_desc})")
            else:
                content.append(f"**Size:** {sizes}")
        
        if 'speed' in race:
            speed = race['speed']
            if isinstance(speed, dict):
                if 'walk' in speed:
                    content.append(f"**Speed:** {speed['walk']} feet")
                else:
                    speed_parts = []
                    for move_type, distance in speed.items():
                        speed_parts.append(f"{move_type} {distance} feet")
                    content.append(f"**Speed:** {', '.join(speed_parts)}")
            else:
                content.append(f"**Speed:** {speed} feet")
        
        # Skill proficiencies
        if 'skillProficiencies' in race:
            skill_profs = race['skillProficiencies']
            if isinstance(skill_profs, list) and skill_profs:
                skill_info = skill_profs[0]
                if 'choose' in skill_info:
                    choose_info = skill_info['choose']
                    count = choose_info.get('count', 1)
                    content.append(f"**Skill Proficiencies:** You gain proficiency in {count} skill{'s' if count > 1 else ''} of your choice")
                elif 'any' in skill_info:
                    count = skill_info['any']
                    content.append(f"**Skill Proficiencies:** You gain proficiency in {count} skill{'s' if count > 1 else ''} of your choice")
        
        # Feats (Origin feats from XPHB)
        if 'feats' in race:
            feats = race['feats']
            if isinstance(feats, list) and feats:
                feat_info = feats[0]
                if 'any' in feat_info:
                    count = feat_info['any']
                    content.append(f"**Feats:** You gain {count} Origin feat{'s' if count > 1 else ''} of your choice")
                elif 'anyFromCategory' in feat_info:
                    category_info = feat_info['anyFromCategory']
                    count = category_info.get('count', 1)
                    content.append(f"**Feats:** You gain {count} Origin feat{'s' if count > 1 else ''} of your choice")
        
        content.append("")
        
        # Racial traits
        if 'entries' in race:
            content.append("## Racial Traits")
            content.append("")
            
            for entry in race['entries']:
                if isinstance(entry, dict):
                    trait_name = entry.get('name', 'Trait')
                    content.append(f"### {trait_name}")
                    
                    if 'entries' in entry:
                        trait_description = self.format_entries(entry['entries'])
                        content.append(trait_description)
                    elif 'entry' in entry:
                        content.append(entry['entry'])
                    
                    content.append("")
                elif isinstance(entry, str):
                    content.append(entry)
                    content.append("")
        
        # Additional traits that might be at root level
        if 'traitTags' in race:
            content.append("## Additional Information")
            content.append("")
            traits = ', '.join(race['traitTags'])
            content.append(f"**Trait Tags:** {traits}")
            content.append("")
        
        # Languages
        if 'languageProficiencies' in race:
            lang_profs = race['languageProficiencies']
            if isinstance(lang_profs, list) and lang_profs:
                content.append("## Languages")
                content.append("")
                for lang_prof in lang_profs:
                    if isinstance(lang_prof, dict):
                        if 'common' in lang_prof:
                            content.append("You can speak, read, and write Common.")
                        if 'choose' in lang_prof:
                            choose_info = lang_prof['choose']
                            count = choose_info.get('count', 1)
                            content.append(f"You can speak, read, and write {count} additional language{'s' if count > 1 else ''} of your choice.")
                content.append("")
        
        # Size details if available
        if 'size' in race and isinstance(race['size'], list):
            for size_info in race['size']:
                if isinstance(size_info, dict) and 'note' in size_info:
                    content.append("## Size")
                    content.append("")
                    content.append(size_info['note'])
                    content.append("")
                    break
        
        # Tags and metadata
        content.extend([
            "---",
            "**Tags:** #5e-reference #race #species",
            f"**Source Data:** `{race.get('_source_file', 'unknown')}` - {source}"
        ])
        
        return '\n'.join(content)

    def extract_cos_references(self) -> Dict[str, List[str]]:
        """Extract all references mentioned in Curse of Strahd adventure."""
        cos_data = self.load_json_data('adventure/adventure-cos.json')
        if not cos_data:
            return {}
        
        references = {
            'creatures': set(),
            'items': set(),
            'spells': set(),
            'locations': set()
        }
        
        # Convert to JSON string and find all references
        cos_text = json.dumps(cos_data)
        
        # Find creature references {@creature Name|Source}
        creature_matches = re.findall(r'\{@creature ([^|]+)(?:\|[^}]+)?\}', cos_text)
        references['creatures'].update(creature_matches)
        
        # Find item references {@item Name|Source}
        item_matches = re.findall(r'\{@item ([^|]+)(?:\|[^}]+)?\}', cos_text)
        references['items'].update(item_matches)
        
        # Find spell references {@spell Name|Source}
        spell_matches = re.findall(r'\{@spell ([^|]+)(?:\|[^}]+)?\}', cos_text)
        references['spells'].update(spell_matches)
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in references.items()}

    def extract_referenced_data(self, extract_type: str, name: str, language: str = 'EN') -> bool:
        """Extract and create reference page for specific data."""
        if extract_type == 'creature':
            data = self.find_creature(name)
            if data:
                content = self.create_creature_page(data, language)
                file_path = self.reference_dir / f"{name.replace(' ', '_')}.md"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created creature reference: {file_path}")
                return True
        
        elif extract_type == 'item':
            data = self.find_item(name)
            if data:
                content = self.create_item_page(data, language)
                file_path = self.reference_dir / f"{name.replace(' ', '_')}.md"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created item reference: {file_path}")
                return True
        
        elif extract_type == 'race':
            data = self.find_race(name)
            if data:
                content = self.create_race_page(data, language)
                file_path = self.reference_dir / f"{name.replace(' ', '_').lower()}.md"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created race reference: {file_path}")
                return True
        
        print(f"Could not find {extract_type}: {name}")
        return False

    def extract_all_cos_data(self):
        """Extract all data referenced in Curse of Strahd."""
        print("Extracting Curse of Strahd references...")
        references = self.extract_cos_references()
        
        total_created = 0
        
        for creature_name in references['creatures']:
            if self.extract_referenced_data('creature', creature_name):
                total_created += 1
        
        for item_name in references['items']:
            if self.extract_referenced_data('item', item_name):
                total_created += 1
        
        # Create index file
        self.create_reference_index(references)
        
        print(f"Extraction complete! Created {total_created} reference files.")

    def create_reference_index(self, references: Dict[str, List[str]]):
        """Create an index file for all references."""
        content = [
            "# 5e Reference Index",
            "",
            "This directory contains extracted D&D 5e data for easy reference in your campaign.",
            "",
            "## Creatures",
            ""
        ]
        
        for creature in references['creatures']:
            filename = creature.replace(' ', '_')
            content.append(f"- [[{filename}|{creature}]]")
        
        content.extend(["", "## Items", ""])
        
        for item in references['items']:
            filename = item.replace(' ', '_')
            content.append(f"- [[{filename}|{item}]]")
        
        content.extend([
            "",
            "---",
            "*Generated by dnd_data_extractor.py*"
        ])
        
        index_path = self.reference_dir / "Index.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"Created reference index: {index_path}")


def main():
    parser = argparse.ArgumentParser(description='Extract D&D 5e data for campaign wiki')
    parser.add_argument('--data-dir', 
                       default='/home/jnunez/Projects/DnD/Vaults/5e-data',
                       help='Path to 5e-data directory')
    parser.add_argument('--vault-dir',
                       default='/home/jnunez/Projects/DnD/Vaults/curse-of-strahd',
                       help='Path to campaign vault directory')
    parser.add_argument('--type', choices=['creature', 'item', 'spell', 'race'],
                       help='Type of data to extract')
    parser.add_argument('--name', help='Name of the creature/item/spell/race to extract')
    parser.add_argument('--extract-cos-data', action='store_true',
                       help='Extract all data referenced in Curse of Strahd')
    parser.add_argument('--language', choices=['EN', 'PT'], default='EN',
                       help='Language for output')
    
    args = parser.parse_args()
    
    # Validate directories
    if not Path(args.data_dir).exists():
        print(f"Error: 5e-data directory not found: {args.data_dir}")
        sys.exit(1)
    
    if not Path(args.vault_dir).exists():
        print(f"Error: Vault directory not found: {args.vault_dir}")
        sys.exit(1)
    
    extractor = DnDDataExtractor(args.data_dir, args.vault_dir)
    
    if args.extract_cos_data:
        extractor.extract_all_cos_data()
    elif args.type and args.name:
        extractor.extract_referenced_data(args.type, args.name, args.language)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()