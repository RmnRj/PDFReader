import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, Any

class NoteGenerator:
    """Generates PDF notes from annotations"""
    
    def __init__(self):
        self.notes_dir = "notes_output"
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        )
        
        # Subheading style
        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.blue
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        )
        
        # Quote style for highlighted text
        self.quote_style = ParagraphStyle(
            'Quote',
            parent=self.styles['Normal'],
            fontSize=9,
            leftIndent=30,
            rightIndent=30,
            spaceAfter=8,
            borderColor=colors.lightgrey,
            borderWidth=1,
            borderPadding=8,
            backColor=colors.lightgrey
        )
    
    def create_notes_pdf(self, pdf_name: str, annotations: Dict[str, Any], 
                        topics: Dict[str, Any]) -> str:
        """Create a comprehensive notes PDF"""
        try:
            # Create output directory
            os.makedirs(self.notes_dir, exist_ok=True)
            
            # Generate output filename
            clean_name = pdf_name.replace('.pdf', '')
            output_filename = f"Notes-{clean_name}.pdf"
            output_path = os.path.join(self.notes_dir, output_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Add title
            title = f"Notes from: {pdf_name}"
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 20))
            
            # Add generation info
            gen_info = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            story.append(Paragraph(gen_info, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Add summary
            self._add_summary(story, pdf_name, annotations, topics)
            
            # Add notes by topic
            if topics:
                self._add_notes_by_topic(story, topics)
            
            # Add all highlights
            if pdf_name in annotations and annotations[pdf_name].get('highlights'):
                self._add_highlights_section(story, annotations[pdf_name]['highlights'])
            
            # Add all comments
            if pdf_name in annotations and annotations[pdf_name].get('comments'):
                self._add_comments_section(story, annotations[pdf_name]['comments'])
            
            # Add individual notes (not organized by topic)
            if pdf_name in annotations and annotations[pdf_name].get('notes'):
                self._add_individual_notes_section(story, annotations[pdf_name]['notes'])
            
            # Build PDF
            doc.build(story)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating notes PDF: {e}")
            return None
    
    def _add_summary(self, story, pdf_name: str, annotations: Dict[str, Any], 
                    topics: Dict[str, Any]):
        """Add summary section to the PDF"""
        story.append(Paragraph("📊 Summary", self.heading_style))
        
        # Count annotations
        pdf_annotations = annotations.get(pdf_name, {})
        highlight_count = len(pdf_annotations.get('highlights', []))
        comment_count = len(pdf_annotations.get('comments', []))
        note_count = len(pdf_annotations.get('notes', []))
        topic_count = len(topics)
        
        summary_data = [
            ['Type', 'Count'],
            ['Topics', str(topic_count)],
            ['Highlights', str(highlight_count)],
            ['Comments', str(comment_count)],
            ['Notes', str(note_count)],
            ['Total Annotations', str(highlight_count + comment_count + note_count)]
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
    
    def _add_notes_by_topic(self, story, topics: Dict[str, Any]):
        """Add notes organized by topic"""
        story.append(Paragraph("📚 Notes by Topic", self.heading_style))
        
        for topic_name, topic_data in topics.items():
            # Topic heading
            story.append(Paragraph(f"🔖 {topic_name}", self.subheading_style))
            
            # Topic notes
            notes = topic_data.get('notes', [])
            if notes:
                for i, note in enumerate(notes, 1):
                    # Note content
                    note_text = f"{i}. {note.get('note', '')}"
                    story.append(Paragraph(note_text, self.body_style))
                    
                    # Original text reference
                    if note.get('text'):
                        ref_text = f"<i>Reference: \"{note['text'][:100]}...\"</i>"
                        story.append(Paragraph(ref_text, self.quote_style))
                    
                    story.append(Spacer(1, 8))
            else:
                story.append(Paragraph("No notes in this topic yet.", self.body_style))
            
            story.append(Spacer(1, 15))
    
    def _add_highlights_section(self, story, highlights: list):
        """Add highlights section"""
        story.append(Paragraph("🖍️ Highlights", self.heading_style))
        
        # Group highlights by color
        color_groups = {}
        for highlight in highlights:
            color = highlight.get('color', 'Unknown')
            if color not in color_groups:
                color_groups[color] = []
            color_groups[color].append(highlight)
        
        for color, color_highlights in color_groups.items():
            # Color subheading
            story.append(Paragraph(f"🎨 {color} Highlights", self.subheading_style))
            
            for i, highlight in enumerate(color_highlights, 1):
                highlight_text = highlight.get('text', '')
                timestamp = highlight.get('timestamp', '')
                
                # Format timestamp
                try:
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%m/%d/%Y %I:%M %p')
                    else:
                        formatted_time = 'Unknown time'
                except:
                    formatted_time = 'Unknown time'
                
                # Add highlight content
                content = f"{i}. {highlight_text}"
                story.append(Paragraph(content, self.quote_style))
                
                # Add timestamp
                time_text = f"<i>Highlighted on: {formatted_time}</i>"
                story.append(Paragraph(time_text, self.body_style))
                story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 15))
    
    def _add_comments_section(self, story, comments: list):
        """Add comments section"""
        story.append(Paragraph("💬 Comments", self.heading_style))
        
        for i, comment in enumerate(comments, 1):
            original_text = comment.get('text', '')
            comment_text = comment.get('comment', '')
            timestamp = comment.get('timestamp', '')
            
            # Format timestamp
            try:
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%m/%d/%Y %I:%M %p')
                else:
                    formatted_time = 'Unknown time'
            except:
                formatted_time = 'Unknown time'
            
            # Comment heading
            story.append(Paragraph(f"Comment #{i}", self.subheading_style))
            
            # Original text
            if original_text:
                story.append(Paragraph("<b>Original Text:</b>", self.body_style))
                story.append(Paragraph(f'"{original_text}"', self.quote_style))
            
            # Comment
            story.append(Paragraph("<b>Comment:</b>", self.body_style))
            story.append(Paragraph(comment_text, self.body_style))
            
            # Timestamp
            time_text = f"<i>Added on: {formatted_time}</i>"
            story.append(Paragraph(time_text, self.body_style))
            story.append(Spacer(1, 15))
    
    def _add_individual_notes_section(self, story, notes: list):
        """Add individual notes section"""
        story.append(Paragraph("📝 Individual Notes", self.heading_style))
        
        for i, note in enumerate(notes, 1):
            original_text = note.get('text', '')
            note_text = note.get('note', '')
            topic = note.get('topic', 'General')
            timestamp = note.get('timestamp', '')
            
            # Format timestamp
            try:
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%m/%d/%Y %I:%M %p')
                else:
                    formatted_time = 'Unknown time'
            except:
                formatted_time = 'Unknown time'
            
            # Note heading
            story.append(Paragraph(f"Note #{i} (Topic: {topic})", self.subheading_style))
            
            # Note content
            story.append(Paragraph(note_text, self.body_style))
            
            # Original text reference
            if original_text:
                story.append(Paragraph("<b>Reference Text:</b>", self.body_style))
                story.append(Paragraph(f'"{original_text[:200]}..."', self.quote_style))
            
            # Timestamp
            time_text = f"<i>Added on: {formatted_time}</i>"
            story.append(Paragraph(time_text, self.body_style))
            story.append(Spacer(1, 15))
    
    def create_topic_summary_pdf(self, pdf_name: str, topic_name: str, 
                                topic_data: Dict[str, Any]) -> str:
        """Create a PDF for a specific topic"""
        try:
            # Create output directory
            os.makedirs(self.notes_dir, exist_ok=True)
            
            # Generate output filename
            clean_pdf_name = pdf_name.replace('.pdf', '')
            clean_topic_name = topic_name.replace(' ', '_')
            output_filename = f"Topic-{clean_topic_name}-{clean_pdf_name}.pdf"
            output_path = os.path.join(self.notes_dir, output_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Add title
            title = f"Topic: {topic_name}"
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 20))
            
            # Add source info
            source_info = f"From: {pdf_name}"
            story.append(Paragraph(source_info, self.styles['Normal']))
            gen_info = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            story.append(Paragraph(gen_info, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Add topic notes
            notes = topic_data.get('notes', [])
            if notes:
                story.append(Paragraph("📝 Notes", self.heading_style))
                for i, note in enumerate(notes, 1):
                    note_text = f"{i}. {note.get('note', '')}"
                    story.append(Paragraph(note_text, self.body_style))
                    
                    if note.get('text'):
                        ref_text = f"<i>Reference: \"{note['text'][:100]}...\"</i>"
                        story.append(Paragraph(ref_text, self.quote_style))
                    
                    story.append(Spacer(1, 10))
            
            # Build PDF
            doc.build(story)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating topic PDF: {e}")
            return None
