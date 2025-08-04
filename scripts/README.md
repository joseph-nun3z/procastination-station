# Campaign Data Scripts

This directory contains scripts for managing and extracting D&D 5e data for your Curse of Strahd campaign.

## dnd_data_extractor.py

A comprehensive script for extracting D&D 5e data from the external 5e-data directory and creating properly formatted Obsidian reference pages.

### Features
- Extracts creatures, items, spells, and other game data
- Creates formatted Obsidian markdown pages with proper linking
- Supports both English and Portuguese output
- Automatically handles cross-references in adventure content
- Generates index files for easy navigation

### Usage Examples

#### Extract a specific creature:
```bash
python scripts/dnd_data_extractor.py --type creature --name "Ismark Kolyanovich"
```

#### Extract a specific item:
```bash
python scripts/dnd_data_extractor.py --type item --name "Longsword"
```

#### Extract all Curse of Strahd referenced data:
```bash
python scripts/dnd_data_extractor.py --extract-cos-data
```

#### Extract in Portuguese:
```bash
python scripts/dnd_data_extractor.py --type creature --name "Veteran" --language PT
```

### Output Structure
All extracted data is saved to `Shared/5e-Reference/` with:
- Individual markdown files for each creature/item/spell
- An `Index.md` file for navigation
- Proper Obsidian linking format
- Source citations for verification

### Configuration
The script uses these default paths:
- **5e-data directory:** `/home/jnunez/Projects/DnD/Vaults/5e-data`
- **Vault directory:** `/home/jnunez/Projects/DnD/Vaults/curse-of-strahd`

Override with `--data-dir` and `--vault-dir` flags if needed.

### Integration with Character Pages
After extracting data, update your character pages to use the new reference format:
- Old: `[[5e-data Reference|Longsword]]`
- New: `[[Shared/5e-Reference/Longsword|Longsword]]`