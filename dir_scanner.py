import os
import fnmatch
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json


def load_dirignore(root_path: Path) -> Set[str]:
    """Load patterns from .dirignore file"""
    patterns = set()
    
    # Always check in current working directory
    dirignore_path = Path.cwd() / '.dirignore'
    
    if dirignore_path.exists():
        print(f"Using .dirignore from: {dirignore_path}")
        with open(dirignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.add(line)
    else:
        print("No .dirignore file found")
    
    return patterns


def should_ignore(path: Path, root_path: Path, patterns: Set[str]) -> bool:
    """Check if path should be ignored based on patterns"""
    relative_path = path.relative_to(root_path)
    path_str = str(relative_path).replace('\\', '/')
    
    for pattern in patterns:
        # Direct match
        if fnmatch.fnmatch(path_str, pattern):
            return True
        
        # Directory pattern (ends with /)
        if pattern.endswith('/'):
            if path.is_dir() and fnmatch.fnmatch(path.name, pattern[:-1]):
                return True
            # Check if any parent matches
            for parent in relative_path.parents:
                if fnmatch.fnmatch(str(parent) + '/', pattern):
                    return True
        
        # Check filename match
        if fnmatch.fnmatch(path.name, pattern):
            return True
            
    return False


def scan_directory(path: Path, root_path: Path, patterns: Set[str]) -> Dict:
    """Recursively scan directory and build structure"""
    structure = {
        'name': path.name,
        'type': 'directory',
        'path': str(path.relative_to(root_path)),
        'children': []
    }
    
    try:
        for item in sorted(path.iterdir()):
            if should_ignore(item, root_path, patterns):
                continue
                
            if item.is_dir():
                structure['children'].append(scan_directory(item, root_path, patterns))
            else:
                structure['children'].append({
                    'name': item.name,
                    'type': 'file',
                    'path': str(item.relative_to(root_path)),
                    'size': item.stat().st_size
                })
                
    except PermissionError:
        structure['error'] = 'Permission denied'
        
    return structure


def print_tree(structure: Dict, prefix: str = '', is_last: bool = True):
    """Print directory structure as tree"""
    connector = '└── ' if is_last else '├── '
    print(prefix + connector + structure['name'])
    
    if structure['type'] == 'directory' and 'children' in structure:
        extension = '    ' if is_last else '│   '
        for i, child in enumerate(structure['children']):
            is_last_child = i == len(structure['children']) - 1
            print_tree(child, prefix + extension, is_last_child)


def export_json(structure: Dict, output_file: str):
    """Export structure to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(structure, f, indent=2)


def get_stats(structure: Dict) -> Dict:
    """Get statistics about the scanned directory"""
    def count_items(node: Dict, stats: Dict):
        if node['type'] == 'file':
            stats['files'] += 1
            size = node.get('size', 0)
            stats['total_size'] += size
            
            # Track file extensions
            ext = os.path.splitext(node['name'])[1].lower()
            if ext:
                stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
                stats['size_by_ext'][ext] = stats['size_by_ext'].get(ext, 0) + size
            
            # Track largest files
            stats['largest_files'].append((node['path'], size))
            stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
            stats['largest_files'] = stats['largest_files'][:10]
            
        else:
            stats['directories'] += 1
            # Track deepest path
            depth = len(Path(node['path']).parts)
            stats['max_depth'] = max(stats['max_depth'], depth)
            
            for child in node.get('children', []):
                count_items(child, stats)
        return stats
    
    initial_stats = {
        'files': 0,
        'directories': 0,
        'total_size': 0,
        'extensions': {},
        'size_by_ext': {},
        'largest_files': [],
        'max_depth': 0
    }
    
    return count_items(structure, initial_stats)


def scan(root_dir: str = '.') -> Dict:
    """Main scanning function"""
    root_path = Path(root_dir).resolve()
    patterns = load_dirignore(root_path)
    return scan_directory(root_path, root_path, patterns)


def main():
    import sys
    
    # Get directory from command line or use current directory
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print(f"Scanning directory: {target_dir}")
    structure = scan(target_dir)
    
    print("\nDirectory Structure:")
    print("=" * 50)
    print_tree(structure)
    
    stats = get_stats(structure)
    print("\n" + "=" * 50)
    print(f"Total files: {stats['files']}")
    print(f"Total directories: {stats['directories']}")
    print(f"Total size: {stats['total_size']:,} bytes ({stats['total_size'] / 1024 / 1024:.2f} MB)")
    print(f"Max depth: {stats['max_depth']}")
    
    if stats['extensions']:
        print("\nFile types:")
        for ext, count in sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True)[:10]:
            size = stats['size_by_ext'][ext]
            print(f"  {ext}: {count} files ({size / 1024:.1f} KB)")
    
    if stats['largest_files']:
        print("\nLargest files:")
        for path, size in stats['largest_files'][:5]:
            print(f"  {path}: {size / 1024:.1f} KB")
    
    # Export to JSON
    export_json(structure, 'directory_structure.json')
    print("\nStructure exported to directory_structure.json")

if __name__ == "__main__":
    main()