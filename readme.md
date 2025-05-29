# Directory Scanner

A simple Python tool that scans directories and creates a structured representation while respecting ignore patterns.

## Quick Start

```bash
# Scan current directory
python dir_scanner.py

# Scan specific directory
python dir_scanner.py /path/to/directory
```

## Features

- 📁 Recursive directory scanning
- 🚫 `.dirignore` file support (like `.gitignore`)
- 🌳 Tree visualization
- 📊 Detailed statistics
- 💾 JSON export

## `.dirignore` File

Create a `.dirignore` file in your working directory:

```
# Comments start with #
__pycache__/
*.pyc
*.log
.env*
node_modules/
dist/
```

### Pattern Examples

| Pattern | Matches |
|---------|---------|
| `*.pyc` | All `.pyc` files |
| `__pycache__/` | All `__pycache__` directories |
| `test_*.py` | Files like `test_unit.py` |
| `.env*` | `.env`, `.env.local`, etc |

## Output

### Console Output
```
Scanning directory: /path/to/project
Using .dirignore from: /current/dir/.dirignore

Directory Structure:
==================================================
└── project
    ├── src
    │   ├── main.py
    │   └── utils.py
    └── README.md

==================================================
Total files: 3
Total directories: 2
Total size: 15,234 bytes (0.01 MB)
Max depth: 2

File types:
  .py: 2 files (12.5 KB)
  .md: 1 files (2.7 KB)

Largest files:
  src/main.py: 8.2 KB
  src/utils.py: 4.3 KB

Structure exported to directory_structure.json
```

### JSON Export

The tool creates `directory_structure.json`:

```json
{
  "name": "project",
  "type": "directory",
  "path": ".",
  "children": [
    {
      "name": "main.py",
      "type": "file",
      "path": "main.py",
      "size": 1234
    }
  ]
}
```

## Use Cases

- **Documentation**: Generate project structure for README files
- **Analysis**: Find large files or deep nesting
- **Cleanup**: Identify file types to ignore
- **Sharing**: Export structure without sharing actual files

## Tips

1. Place `.dirignore` where you run the script
2. Use wildcards for flexible patterns
3. Check JSON output for programmatic access
4. Pipe output to file: `python dir_scanner.py > structure.txt`