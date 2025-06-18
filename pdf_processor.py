import pdfplumber
import re
from typing import List, Dict, Any

class PDFProcessor:
    """Handles PDF processing operations including text extraction and search"""
    
    def __init__(self):
        self.current_pdf_path = None
        self.pages_cache = {}
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n--- Page {page_num + 1} ---\n"
                        full_text += page_text + "\n"
                        
                        # Cache page text for later use
                        self.pages_cache[page_num] = {
                            'text': page_text,
                            'page_num': page_num + 1
                        }
            
            self.current_pdf_path = pdf_path
            return full_text
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_by_page(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF file page by page"""
        try:
            pages = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages.append({
                            'page_num': page_num + 1,
                            'text': page_text,
                            'word_count': len(page_text.split())
                        })
            return pages
            
        except Exception as e:
            raise Exception(f"Error extracting pages from PDF: {str(e)}")
    
    def search_text(self, text: str, query: str, case_sensitive: bool = False) -> List[str]:
        """Search for text within the PDF content"""
        if not query.strip():
            return []
        
        try:
            # Prepare search parameters
            search_text = text if case_sensitive else text.lower()
            search_query = query if case_sensitive else query.lower()
            
            # Find all matches with context
            results = []
            lines = search_text.split('\n')
            
            for line_num, line in enumerate(lines):
                if search_query in line:
                    # Get context around the match (3 lines before and after)
                    start_line = max(0, line_num - 3)
                    end_line = min(len(lines), line_num + 4)
                    
                    context_lines = lines[start_line:end_line]
                    context = '\n'.join(context_lines)
                    
                    # Highlight the search term in the result
                    highlighted_context = self._highlight_search_term(context, query, case_sensitive)
                    results.append(highlighted_context)
            
            return results
            
        except Exception as e:
            return []
    
    def _highlight_search_term(self, text: str, term: str, case_sensitive: bool = False) -> str:
        """Highlight search term in text"""
        if case_sensitive:
            pattern = re.escape(term)
        else:
            pattern = re.escape(term)
            text_to_search = text
        
        try:
            if case_sensitive:
                highlighted = re.sub(
                    f'({pattern})',
                    r'**\1**',
                    text
                )
            else:
                highlighted = re.sub(
                    f'({pattern})',
                    r'**\1**',
                    text,
                    flags=re.IGNORECASE
                )
            return highlighted
        except:
            return text
    
    def extract_topics_from_text(self, text: str) -> List[str]:
        """Extract potential topics from text using simple heuristics"""
        try:
            topics = []
            
            # Look for common topic indicators
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and page markers
                if not line or line.startswith('--- Page'):
                    continue
                
                # Look for lines that might be headings/topics
                # 1. Short lines (likely titles)
                # 2. Lines with specific formatting patterns
                # 3. Lines that start with numbers or bullets
                
                if len(line) < 100:  # Potential heading
                    # Check if it looks like a heading
                    if (line.isupper() or 
                        line.startswith(('Chapter', 'Section', 'Part')) or
                        re.match(r'^\d+\.?\s+[A-Z]', line) or
                        line.endswith(':') or
                        len(line.split()) <= 8):
                        
                        # Clean up the topic
                        topic = re.sub(r'^\d+\.?\s*', '', line)  # Remove leading numbers
                        topic = topic.rstrip(':')  # Remove trailing colons
                        topic = topic.strip()
                        
                        if len(topic) > 2 and topic not in topics:
                            topics.append(topic)
            
            return topics[:20]  # Return top 20 potential topics
            
        except Exception as e:
            return []
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 2000) -> List[str]:
        """Split text into smaller chunks for better display"""
        if not text:
            return []
        
        try:
            # Split by pages first
            pages = text.split('--- Page')
            chunks = []
            
            for page in pages:
                if not page.strip():
                    continue
                
                # If page is small enough, add as single chunk
                if len(page) <= chunk_size:
                    chunks.append(page.strip())
                else:
                    # Split large pages into smaller chunks
                    words = page.split()
                    current_chunk = []
                    current_length = 0
                    
                    for word in words:
                        word_length = len(word) + 1  # +1 for space
                        
                        if current_length + word_length > chunk_size and current_chunk:
                            chunks.append(' '.join(current_chunk))
                            current_chunk = [word]
                            current_length = word_length
                        else:
                            current_chunk.append(word)
                            current_length += word_length
                    
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
            
            return chunks if chunks else [text]
            
        except Exception as e:
            return [text]
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Get basic statistics about the text"""
        try:
            words = text.split()
            lines = text.split('\n')
            
            # Count pages
            page_count = text.count('--- Page')
            
            # Estimate reading time (average 200 words per minute)
            reading_time_minutes = len(words) / 200
            
            return {
                'word_count': len(words),
                'character_count': len(text),
                'line_count': len(lines),
                'page_count': page_count,
                'estimated_reading_time': f"{reading_time_minutes:.1f} minutes"
            }
            
        except Exception as e:
            return {
                'word_count': 0,
                'character_count': 0,
                'line_count': 0,
                'page_count': 0,
                'estimated_reading_time': "Unknown"
            }
