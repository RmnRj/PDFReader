import streamlit as st
import os
import json
from pdf_processor import PDFProcessor
from annotation_manager import AnnotationManager
from note_generator import NoteGenerator
from utils import create_directories, get_color_options

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_pdf' not in st.session_state:
        st.session_state.current_pdf = None
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = ""
    if 'annotations' not in st.session_state:
        st.session_state.annotations = {}
    if 'topics' not in st.session_state:
        st.session_state.topics = {}
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "Portrait"
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0

def main():
    st.set_page_config(
        page_title="PDF Reader with Annotations",
        page_icon="📖",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Create necessary directories
    create_directories()
    
    # Initialize processors
    pdf_processor = PDFProcessor()
    annotation_manager = AnnotationManager()
    note_generator = NoteGenerator()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("📖 PDF Reader Controls")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload PDF File",
            type=['pdf'],
            help="Select a PDF file to read and annotate"
        )
        
        if uploaded_file is not None:
            if st.session_state.current_pdf != uploaded_file.name:
                # Process new PDF
                st.session_state.current_pdf = uploaded_file.name
                
                # Save uploaded file
                with open(f"temp_{uploaded_file.name}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Extract text and process PDF
                with st.spinner("Processing PDF..."):
                    st.session_state.pdf_text = pdf_processor.extract_text(f"temp_{uploaded_file.name}")
                    st.session_state.annotations = annotation_manager.load_annotations(uploaded_file.name)
                    st.session_state.topics = annotation_manager.load_topics(uploaded_file.name)
                
                st.success(f"Loaded: {uploaded_file.name}")
        
        # View mode selection
        st.subheader("📱 View Mode")
        view_mode = st.radio(
            "Select view mode:",
            ["Portrait", "Landscape"],
            index=0 if st.session_state.view_mode == "Portrait" else 1
        )
        st.session_state.view_mode = view_mode
        
        # Search functionality
        st.subheader("🔍 Search")
        search_query = st.text_input(
            "Search in document:",
            value=st.session_state.search_query,
            placeholder="Enter search term..."
        )
        st.session_state.search_query = search_query
        
        if search_query and st.session_state.pdf_text:
            search_results = pdf_processor.search_text(st.session_state.pdf_text, search_query)
            if search_results:
                st.write(f"Found {len(search_results)} results")
                for i, result in enumerate(search_results[:5]):  # Show first 5 results
                    if st.button(f"Result {i+1}: ...{result[:50]}...", key=f"search_{i}"):
                        st.session_state.selected_text = result
            else:
                st.write("No results found")
        
        # Topic management
        st.subheader("📚 Topics")
        if st.session_state.topics:
            for topic_name, topic_data in st.session_state.topics.items():
                with st.expander(f"📝 {topic_name}"):
                    st.write(f"Notes: {len(topic_data.get('notes', []))}")
                    st.write(f"Highlights: {len(topic_data.get('highlights', []))}")
                    st.write(f"Comments: {len(topic_data.get('comments', []))}")
        
        # Export notes
        if st.session_state.current_pdf and st.session_state.annotations:
            if st.button("💾 Export Notes"):
                with st.spinner("Generating notes PDF..."):
                    note_file = note_generator.create_notes_pdf(
                        st.session_state.current_pdf,
                        st.session_state.annotations,
                        st.session_state.topics
                    )
                    if note_file and os.path.exists(note_file):
                        with open(note_file, "rb") as f:
                            st.download_button(
                                label="📥 Download Notes PDF",
                                data=f.read(),
                                file_name=f"Notes-{st.session_state.current_pdf}",
                                mime="application/pdf"
                            )
                        st.success("Notes PDF generated successfully!")
    
    # Main content area
    if st.session_state.current_pdf and st.session_state.pdf_text:
        # Header with PDF name and controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.header(f"📖 {st.session_state.current_pdf}")
        with col2:
            st.metric("View Mode", st.session_state.view_mode)
        with col3:
            st.metric("Pages", "PDF Loaded")
        
        # Text selection and annotation interface
        st.subheader("✏️ Text Selection & Annotation")
        
        # Text area for displaying PDF content with line numbers
        text_area_height = 400 if st.session_state.view_mode == "Portrait" else 300
        
        # Split text into manageable chunks for display
        text_chunks = pdf_processor.split_text_into_chunks(st.session_state.pdf_text, 2000)
        
        # Page navigation
        if len(text_chunks) > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page = max(0, st.session_state.current_page - 1)
                    st.rerun()
            with col2:
                st.write(f"Section {st.session_state.current_page + 1} of {len(text_chunks)}")
            with col3:
                if st.button("➡️ Next", disabled=st.session_state.current_page >= len(text_chunks) - 1):
                    st.session_state.current_page = min(len(text_chunks) - 1, st.session_state.current_page + 1)
                    st.rerun()
        
        # Display current text chunk
        current_text = text_chunks[st.session_state.current_page] if text_chunks else st.session_state.pdf_text
        
        # Text selection area
        selected_text = st.text_area(
            "Select text to annotate (copy the text you want to highlight/comment on):",
            value=st.session_state.selected_text,
            height=150,
            help="Copy and paste the text you want to annotate from the document below"
        )
        st.session_state.selected_text = selected_text
        
        # Annotation controls
        if selected_text.strip():
            st.subheader("🎨 Annotation Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Highlighting
                st.write("**Highlight Options:**")
                highlight_colors = get_color_options()
                selected_color = st.selectbox(
                    "Choose highlight color:",
                    options=list(highlight_colors.keys()),
                    format_func=lambda x: f"{x} {highlight_colors[x]['emoji']}"
                )
                
                if st.button("🖍️ Add Highlight", type="primary"):
                    annotation_manager.add_highlight(
                        st.session_state.current_pdf,
                        selected_text,
                        selected_color,
                        st.session_state.annotations
                    )
                    st.success(f"Added {selected_color.lower()} highlight!")
                    st.rerun()
            
            with col2:
                # Comments and Notes
                st.write("**Comments & Notes:**")
                comment_text = st.text_area(
                    "Add comment:",
                    placeholder="Enter your comment here...",
                    height=80
                )
                
                if st.button("💬 Add Comment") and comment_text.strip():
                    annotation_manager.add_comment(
                        st.session_state.current_pdf,
                        selected_text,
                        comment_text,
                        st.session_state.annotations
                    )
                    st.success("Comment added!")
                    st.rerun()
                
                # Topic assignment
                topic_name = st.text_input(
                    "Assign to topic:",
                    placeholder="Enter topic name..."
                )
                
                note_text = st.text_area(
                    "Add note:",
                    placeholder="Enter your note here...",
                    height=80
                )
                
                if st.button("📝 Add Note") and note_text.strip():
                    if not topic_name.strip():
                        topic_name = "General Notes"
                    
                    annotation_manager.add_note(
                        st.session_state.current_pdf,
                        selected_text,
                        note_text,
                        topic_name,
                        st.session_state.annotations,
                        st.session_state.topics
                    )
                    st.success(f"Note added to topic: {topic_name}")
                    st.rerun()
        
        # Display PDF text with annotations
        st.subheader("📄 Document Content")
        
        # Apply view mode styling
        if st.session_state.view_mode == "Landscape":
            st.markdown(
                """
                <style>
                .stTextArea textarea {
                    font-size: 14px !important;
                    line-height: 1.4 !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        
        # Display text with highlights
        annotated_text = annotation_manager.apply_highlights_to_text(
            current_text,
            st.session_state.annotations.get(st.session_state.current_pdf, {})
        )
        
        st.markdown(annotated_text, unsafe_allow_html=True)
        
        # Show existing annotations
        if st.session_state.current_pdf in st.session_state.annotations:
            annotations = st.session_state.annotations[st.session_state.current_pdf]
            
            if annotations.get('highlights') or annotations.get('comments') or annotations.get('notes'):
                st.subheader("📋 Current Annotations")
                
                # Highlights
                if annotations.get('highlights'):
                    with st.expander(f"🖍️ Highlights ({len(annotations['highlights'])})"):
                        for i, highlight in enumerate(annotations['highlights']):
                            color_info = get_color_options()[highlight['color']]
                            st.markdown(
                                f"<div style='background-color: {color_info['hex']}; padding: 8px; margin: 4px 0; border-radius: 4px;'>"
                                f"<strong>{highlight['color']} {color_info['emoji']}</strong><br>"
                                f"{highlight['text'][:100]}...</div>",
                                unsafe_allow_html=True
                            )
                
                # Comments
                if annotations.get('comments'):
                    with st.expander(f"💬 Comments ({len(annotations['comments'])})"):
                        for comment in annotations['comments']:
                            st.write(f"**Text:** {comment['text'][:50]}...")
                            st.write(f"**Comment:** {comment['comment']}")
                            st.divider()
                
                # Notes by topic
                if st.session_state.topics:
                    with st.expander(f"📝 Notes by Topic ({len(st.session_state.topics)})"):
                        for topic_name, topic_data in st.session_state.topics.items():
                            st.write(f"**📚 {topic_name}**")
                            for note in topic_data.get('notes', []):
                                st.write(f"• {note['note']}")
                            st.divider()
    
    else:
        # Welcome screen
        st.title("📖 PDF Reader with Annotations")
        st.markdown("""
        ### Welcome to your PDF annotation tool!
        
        **Features:**
        - 📄 Upload and read PDF files
        - 🖍️ Highlight text with multiple colors
        - 💬 Add comments to selected text
        - 📝 Take organized notes by topic
        - 🔍 Search within documents
        - 📱 Portrait and landscape viewing modes
        - 💾 Export notes to separate PDF files
        
        **How to use:**
        1. Upload a PDF file using the sidebar
        2. Select text you want to annotate
        3. Choose highlight colors, add comments, or create notes
        4. Organize your thoughts by topics
        5. Export your annotations as a separate PDF
        
        Start by uploading a PDF file from the sidebar! 👈
        """)

if __name__ == "__main__":
    main()
