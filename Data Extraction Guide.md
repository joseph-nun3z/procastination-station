# 5e Data Extraction Guide

This guide explains how to use the `dnd_data_extractor.py` script to pull D&D 5e data from your external 5e-data directory into your campaign vault for proper Obsidian linking.

## Quick Start

### Extract Individual Items
```bash
# Extract a specific creature
python scripts/dnd_data_extractor.py --type creature --name "Strahd von Zarovich"

# Extract a specific item  
python scripts/dnd_data_extractor.py --type item --name "Holy Symbol of Ravenkind"

# Extract a specific spell
python scripts/dnd_data_extractor.py --type spell --name "Turn Undead"
```

### Extract All CoS References
```bash
# This will scan the adventure and extract all referenced creatures, items, etc.
python scripts/dnd_data_extractor.py --extract-cos-data
```

## How It Works

1. **Scans External Data**: The script reads JSON files from `/home/jnunez/Projects/DnD/Vaults/5e-data/data/`

2. **Creates Local References**: Extracts the data and creates formatted markdown files in `Shared/5e-Reference/`

3. **Formats for Obsidian**: Uses proper markdown formatting with Obsidian-compatible links

4. **Maintains Source Attribution**: Each page includes source citations and file references

## Linking in Your Campaign Pages

After extracting data, update your character/location pages to use the local references:

### Before (Placeholder Links):
```markdown
- **Weapon:** [[5e-data Reference|Longsword]]
- **Stats:** Based on [[5e-data Reference|Veteran]] stat block
```

### After (Local References):
```markdown
- **Weapon:** [[Shared/5e-Reference/Longsword|Longsword]]  
- **Stats:** Based on [[Shared/5e-Reference/Veteran|Veteran]] stat block
```

## Reference Structure

All extracted references are stored in:
```
Shared/5e-Reference/
├── Index.md                    # Navigation index
├── Strahd_von_Zarovich.md     # Creatures
├── Longsword.md               # Items  
├── Veteran.md                 # Stat blocks
└── ...
```

## Extracted Data Includes

### Creatures
- Full stat blocks (AC, HP, abilities, etc.)
- Actions and special abilities
- Source page references
- Proper tags for organization

### Items
- Type, rarity, value, weight
- Magical properties
- Attunement requirements
- Mechanical effects

### Spells
- Level, school, components
- Casting time and range
- Description and effects
- Class availability

## Multi-Language Support

The script supports both English and Portuguese output:

```bash
# Extract in Portuguese
python scripts/dnd_data_extractor.py --type creature --name "Veteran" --language PT
```

## Tips for Campaign Integration

1. **Extract Early**: Run the extraction before creating character pages to have all references ready

2. **Use Index**: The generated `Index.md` provides easy navigation to all extracted data

3. **Link Consistently**: Always use the full path format: `[[Shared/5e-Reference/Name|Display Name]]`

4. **Update Templates**: Modify your NPC/location templates to use the new reference format

5. **Verify Links**: After extraction, check that all links resolve properly in Obsidian

## Common Extractions for CoS

Some key data you'll want to extract:

```bash
# Major NPCs
python scripts/dnd_data_extractor.py --type creature --name "Strahd von Zarovich"
python scripts/dnd_data_extractor.py --type creature --name "Ireena Kolyana"
python scripts/dnd_data_extractor.py --type creature --name "Rahadin"

# Important Items
python scripts/dnd_data_extractor.py --type item --name "Sunsword"
python scripts/dnd_data_extractor.py --type item --name "Holy Symbol of Ravenkind"
python scripts/dnd_data_extractor.py --type item --name "Tome of Strahd"

# Common Stat Blocks
python scripts/dnd_data_extractor.py --type creature --name "Vampire Spawn"
python scripts/dnd_data_extractor.py --type creature --name "Dire Wolf"
```

This creates a robust, locally-referenced system that works offline and integrates seamlessly with your Obsidian campaign vault!