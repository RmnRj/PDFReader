import os
from typing import Dict, Any

def create_directories():
    """Create necessary directories for the application"""
    directories = [
        "annotations",
        "topics", 
        "notes_output",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_color_options() -> Dict[str, Dict[str, str]]:
    """Get available highlight color options"""
    return {
        'Light Green': {
            'hex': '#90EE90',
            'emoji': '🟢'
        },
        'Light Yellow': {
            'hex': '#FFFFE0', 
            'emoji': '🟡'
        },
        'Light Blue': {
            'hex': '#ADD8E6',
            'emoji': '🔵'
        },
        'Light Pink': {
            'hex': '#FFB6C1',
            'emoji': '🩷'
        },
        'Light Red': {
            'hex': '#FFA07A',
            'emoji': '🔴'
        }
    }

def clean_filename(filename: str) -> str:
    """Clean filename for safe file system operations"""
    import re
    # Remove or replace unsafe characters
    cleaned = re.sub(r'[^\w\-_\.]', '_', filename)
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    return cleaned

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp string for display"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return 'Unknown time'

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def validate_pdf_file(file_path: str) -> bool:
    """Validate if file is a valid PDF"""
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            # Try to get first page to validate
            if len(pdf.pages) > 0:
                return True
        return False
    except:
        return False

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    except:
        return 0.0

def search_text_with_context(text: str, query: str, context_lines: int = 3) -> list:
    """Search text and return results with context"""
    if not query.strip():
        return []
    
    results = []
    lines = text.split('\n')
    query_lower = query.lower()
    
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            # Get context
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            
            context = lines[start:end]
            context_text = '\n'.join(context)
            
            # Highlight the search term
            highlighted_line = line.replace(
                query, 
                f"**{query}**"
            )
            context[i - start] = highlighted_line
            
            results.append({
                'line_number': i + 1,
                'context': '\n'.join(context),
                'highlighted_line': highlighted_line
            })
    
    return results

def export_annotations_json(pdf_name: str, annotations: Dict[str, Any], 
                           topics: Dict[str, Any]) -> str:
    """Export annotations to JSON file"""
    try:
        import json
        from datetime import datetime
        
        export_data = {
            'pdf_name': pdf_name,
            'export_date': datetime.now().isoformat(),
            'annotations': annotations.get(pdf_name, {}),
            'topics': topics
        }
        
        clean_name = clean_filename(pdf_name.replace('.pdf', ''))
        export_filename = f"annotations_export_{clean_name}.json"
        export_path = os.path.join("notes_output", export_filename)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return export_path
    except Exception as e:
        print(f"Error exporting annotations: {e}")
        return None

def import_annotations_json(import_path: str) -> tuple:
    """Import annotations from JSON file"""
    try:
        import json
        
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pdf_name = data.get('pdf_name', 'Unknown')
        annotations = {pdf_name: data.get('annotations', {})}
        topics = data.get('topics', {})
        
        return pdf_name, annotations, topics
    except Exception as e:
        print(f"Error importing annotations: {e}")
        return None, {}, {}

def get_reading_statistics(text: str) -> Dict[str, Any]:
    """Get reading statistics for text"""
    try:
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        # Estimate reading time (average 200 words per minute)
        reading_time_minutes = len(words) / 200
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'character_count': len(text),
            'character_count_no_spaces': len(text.replace(' ', '')),
            'estimated_reading_time_minutes': round(reading_time_minutes, 1),
            'estimated_reading_time_formatted': f"{int(reading_time_minutes)} min {int((reading_time_minutes % 1) * 60)} sec"
        }
    except Exception as e:
        return {
            'word_count': 0,
            'sentence_count': 0, 
            'paragraph_count': 0,
            'character_count': 0,
            'character_count_no_spaces': 0,
            'estimated_reading_time_minutes': 0,
            'estimated_reading_time_formatted': '0 min 0 sec'
        }
