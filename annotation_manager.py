import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any

class AnnotationManager:
    """Manages annotations including highlights, comments, and notes"""
    
    def __init__(self):
        self.annotations_dir = "annotations"
        self.topics_dir = "topics"
        
    def get_annotation_file_path(self, pdf_name: str) -> str:
        """Get the path for annotations file"""
        clean_name = re.sub(r'[^\w\-_\.]', '_', pdf_name)
        return os.path.join(self.annotations_dir, f"{clean_name}_annotations.json")
    
    def get_topics_file_path(self, pdf_name: str) -> str:
        """Get the path for topics file"""
        clean_name = re.sub(r'[^\w\-_\.]', '_', pdf_name)
        return os.path.join(self.topics_dir, f"{clean_name}_topics.json")
    
    def load_annotations(self, pdf_name: str) -> Dict[str, Any]:
        """Load existing annotations for a PDF"""
        try:
            annotations_file = self.get_annotation_file_path(pdf_name)
            if os.path.exists(annotations_file):
                with open(annotations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading annotations: {e}")
            return {}
    
    def save_annotations(self, pdf_name: str, annotations: Dict[str, Any]) -> bool:
        """Save annotations for a PDF"""
        try:
            annotations_file = self.get_annotation_file_path(pdf_name)
            os.makedirs(os.path.dirname(annotations_file), exist_ok=True)
            
            with open(annotations_file, 'w', encoding='utf-8') as f:
                json.dump(annotations, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving annotations: {e}")
            return False
    
    def load_topics(self, pdf_name: str) -> Dict[str, Any]:
        """Load existing topics for a PDF"""
        try:
            topics_file = self.get_topics_file_path(pdf_name)
            if os.path.exists(topics_file):
                with open(topics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading topics: {e}")
            return {}
    
    def save_topics(self, pdf_name: str, topics: Dict[str, Any]) -> bool:
        """Save topics for a PDF"""
        try:
            topics_file = self.get_topics_file_path(pdf_name)
            os.makedirs(os.path.dirname(topics_file), exist_ok=True)
            
            with open(topics_file, 'w', encoding='utf-8') as f:
                json.dump(topics, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving topics: {e}")
            return False
    
    def add_highlight(self, pdf_name: str, text: str, color: str, annotations: Dict[str, Any]) -> bool:
        """Add a highlight annotation"""
        try:
            if pdf_name not in annotations:
                annotations[pdf_name] = {
                    'highlights': [],
                    'comments': [],
                    'notes': []
                }
            
            highlight = {
                'id': len(annotations[pdf_name].get('highlights', [])) + 1,
                'text': text.strip(),
                'color': color,
                'timestamp': datetime.now().isoformat(),
                'text_preview': text.strip()[:100] + "..." if len(text.strip()) > 100 else text.strip()
            }
            
            annotations[pdf_name]['highlights'].append(highlight)
            return self.save_annotations(pdf_name, annotations)
            
        except Exception as e:
            print(f"Error adding highlight: {e}")
            return False
    
    def add_comment(self, pdf_name: str, text: str, comment: str, annotations: Dict[str, Any]) -> bool:
        """Add a comment annotation"""
        try:
            if pdf_name not in annotations:
                annotations[pdf_name] = {
                    'highlights': [],
                    'comments': [],
                    'notes': []
                }
            
            comment_annotation = {
                'id': len(annotations[pdf_name].get('comments', [])) + 1,
                'text': text.strip(),
                'comment': comment.strip(),
                'timestamp': datetime.now().isoformat(),
                'text_preview': text.strip()[:100] + "..." if len(text.strip()) > 100 else text.strip()
            }
            
            annotations[pdf_name]['comments'].append(comment_annotation)
            return self.save_annotations(pdf_name, annotations)
            
        except Exception as e:
            print(f"Error adding comment: {e}")
            return False
    
    def add_note(self, pdf_name: str, text: str, note: str, topic: str, 
                 annotations: Dict[str, Any], topics: Dict[str, Any]) -> bool:
        """Add a note annotation and organize by topic"""
        try:
            # Add to annotations
            if pdf_name not in annotations:
                annotations[pdf_name] = {
                    'highlights': [],
                    'comments': [],
                    'notes': []
                }
            
            note_annotation = {
                'id': len(annotations[pdf_name].get('notes', [])) + 1,
                'text': text.strip(),
                'note': note.strip(),
                'topic': topic.strip(),
                'timestamp': datetime.now().isoformat(),
                'text_preview': text.strip()[:100] + "..." if len(text.strip()) > 100 else text.strip()
            }
            
            annotations[pdf_name]['notes'].append(note_annotation)
            
            # Add to topics
            if topic not in topics:
                topics[topic] = {
                    'name': topic,
                    'created': datetime.now().isoformat(),
                    'notes': [],
                    'highlights': [],
                    'comments': []
                }
            
            topics[topic]['notes'].append({
                'note': note.strip(),
                'text': text.strip(),
                'timestamp': datetime.now().isoformat(),
                'note_id': note_annotation['id']
            })
            
            # Save both
            success1 = self.save_annotations(pdf_name, annotations)
            success2 = self.save_topics(pdf_name, topics)
            
            return success1 and success2
            
        except Exception as e:
            print(f"Error adding note: {e}")
            return False
    
    def apply_highlights_to_text(self, text: str, annotations: Dict[str, Any]) -> str:
        """Apply highlight styling to text"""
        try:
            if not annotations or 'highlights' not in annotations:
                return text
            
            # Create a copy of text to modify
            highlighted_text = text
            
            # Color mapping
            color_map = {
                'Light Green': '#90EE90',
                'Light Yellow': '#FFFFE0',
                'Light Blue': '#ADD8E6',
                'Light Pink': '#FFB6C1',
                'Light Red': '#FFA07A'
            }
            
            # Sort highlights by text length (longest first) to avoid nested highlighting issues
            highlights = sorted(annotations['highlights'], key=lambda x: len(x['text']), reverse=True)
            
            for highlight in highlights:
                highlight_text = highlight['text'].strip()
                color = highlight['color']
                bg_color = color_map.get(color, '#FFFFE0')
                
                # Create highlighted version
                highlighted_version = f'<mark style="background-color: {bg_color}; padding: 2px 4px; border-radius: 3px; margin: 1px;">{highlight_text}</mark>'
                
                # Replace in text (only first occurrence to avoid duplicates)
                if highlight_text in highlighted_text:
                    highlighted_text = highlighted_text.replace(highlight_text, highlighted_version, 1)
            
            return highlighted_text
            
        except Exception as e:
            print(f"Error applying highlights: {e}")
            return text
    
    def get_annotation_summary(self, pdf_name: str) -> Dict[str, Any]:
        """Get summary of all annotations for a PDF"""
        try:
            annotations = self.load_annotations(pdf_name)
            topics = self.load_topics(pdf_name)
            
            if pdf_name not in annotations:
                return {
                    'total_highlights': 0,
                    'total_comments': 0,
                    'total_notes': 0,
                    'total_topics': 0,
                    'last_modified': None
                }
            
            pdf_annotations = annotations[pdf_name]
            
            # Get latest timestamp
            all_timestamps = []
            for item_list in [pdf_annotations.get('highlights', []), 
                             pdf_annotations.get('comments', []), 
                             pdf_annotations.get('notes', [])]:
                for item in item_list:
                    if 'timestamp' in item:
                        all_timestamps.append(item['timestamp'])
            
            last_modified = max(all_timestamps) if all_timestamps else None
            
            return {
                'total_highlights': len(pdf_annotations.get('highlights', [])),
                'total_comments': len(pdf_annotations.get('comments', [])),
                'total_notes': len(pdf_annotations.get('notes', [])),
                'total_topics': len(topics),
                'last_modified': last_modified
            }
            
        except Exception as e:
            print(f"Error getting annotation summary: {e}")
            return {
                'total_highlights': 0,
                'total_comments': 0,
                'total_notes': 0,
                'total_topics': 0,
                'last_modified': None
            }
    
    def delete_annotation(self, pdf_name: str, annotation_type: str, annotation_id: int, 
                         annotations: Dict[str, Any]) -> bool:
        """Delete a specific annotation"""
        try:
            if pdf_name not in annotations or annotation_type not in annotations[pdf_name]:
                return False
            
            # Find and remove the annotation
            annotations_list = annotations[pdf_name][annotation_type]
            annotations[pdf_name][annotation_type] = [
                ann for ann in annotations_list if ann.get('id') != annotation_id
            ]
            
            return self.save_annotations(pdf_name, annotations)
            
        except Exception as e:
            print(f"Error deleting annotation: {e}")
            return False
    
    def search_annotations(self, pdf_name: str, query: str) -> Dict[str, List[Any]]:
        """Search through annotations"""
        try:
            annotations = self.load_annotations(pdf_name)
            topics = self.load_topics(pdf_name)
            
            if pdf_name not in annotations:
                return {'highlights': [], 'comments': [], 'notes': [], 'topics': []}
            
            query_lower = query.lower()
            results = {
                'highlights': [],
                'comments': [],
                'notes': [],
                'topics': []
            }
            
            pdf_annotations = annotations[pdf_name]
            
            # Search highlights
            for highlight in pdf_annotations.get('highlights', []):
                if query_lower in highlight.get('text', '').lower():
                    results['highlights'].append(highlight)
            
            # Search comments
            for comment in pdf_annotations.get('comments', []):
                if (query_lower in comment.get('text', '').lower() or 
                    query_lower in comment.get('comment', '').lower()):
                    results['comments'].append(comment)
            
            # Search notes
            for note in pdf_annotations.get('notes', []):
                if (query_lower in note.get('text', '').lower() or 
                    query_lower in note.get('note', '').lower() or
                    query_lower in note.get('topic', '').lower()):
                    results['notes'].append(note)
            
            # Search topics
            for topic_name, topic_data in topics.items():
                if query_lower in topic_name.lower():
                    results['topics'].append(topic_data)
                else:
                    # Search within topic notes
                    for note in topic_data.get('notes', []):
                        if query_lower in note.get('note', '').lower():
                            results['topics'].append(topic_data)
                            break
            
            return results
            
        except Exception as e:
            print(f"Error searching annotations: {e}")
            return {'highlights': [], 'comments': [], 'notes': [], 'topics': []}
