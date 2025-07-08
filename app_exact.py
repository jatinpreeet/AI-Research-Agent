import streamlit as st
import os
import operator
from typing import List, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, get_buffer_string
from langchain_tavily import TavilySearch
from langchain_community.document_loaders import WikipediaLoader
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
import time
import base64
import re
from io import BytesIO
try:
    import weasyprint
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    
# Fallback imports for reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configure the page
st.set_page_config(
    page_title="Research.ai",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Perplexity-inspired clean CSS
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding: 0;
        max-width: 100%;
        background: #0f0f0f;
        min-height: 100vh;
    }
    
    /* Main content area */
    .chat-area {
        max-width: 768px;
        margin: 0 auto;
        padding: 1.5rem;
        min-height: 100vh;
        transition: all 0.3s ease;
    }
    
    /* Chat area when empty (centered) */
    .chat-area.empty {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 2rem;
    }
    
    /* Chat area with messages (top aligned) */
    .chat-area.has-messages {
        padding: 2rem 1.5rem 8rem 1.5rem;
        min-height: auto;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .empty-title {
        font-family: 'Orbitron', 'Inter', monospace;
        font-size: 3rem;
        font-weight: 700;
        color: #06b6d4;
        margin-bottom: 0.5rem;
        letter-spacing: 0.1em;
        text-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .empty-subtitle {
        font-size: 1.125rem;
        color: #64748b;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Messages */
    .message {
        margin-bottom: 1.25rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
    }
    
    .user-message-content {
        background: #374151;
        border: 1px solid #4b5563;
        border-radius: 18px;
        padding: 0.75rem 1rem;
        max-width: 75%;
        font-size: 0.9rem;
        line-height: 1.4;
        color: #f9fafb;
    }
    
    .assistant-message {
        margin-bottom: 1.25rem;
    }
    
    .assistant-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #9ca3af;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .assistant-content {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 1.25rem;
        font-size: 0.9rem;
        line-height: 1.6;
        color: #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress indicator */
    .progress-message {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 0.625rem 0.875rem;
        margin: 0.75rem 0;
        color: #06b6d4;
        font-size: 0.8rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input area - centered when empty */
    .input-container.empty {
        position: static;
        background: transparent;
        border: none;
        padding: 0;
        z-index: auto;
    }
    
    /* Input area - fixed when has messages */
    .input-container.has-messages {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(15, 15, 15, 0.95);
        backdrop-filter: blur(10px);
        border-top: 1px solid #374151;
        padding: 0.75rem;
        z-index: 1000;
    }
    
    .input-wrapper {
        max-width: 768px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }
    
    /* Input styling */
    .stTextArea textarea {
        border: 1px solid #d1d5db !important;
        border-radius: 24px !important;
        padding: 0.875rem 1rem !important;
        font-size: 0.9rem !important;
        line-height: 1.4 !important;
        resize: none !important;
        background: white !important;
        color: #1f2937 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        font-family: 'Inter', sans-serif !important;
        min-height: 68px !important;
    }
    
    .stTextArea textarea:focus {
        outline: none !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #9ca3af !important;
    }
    
    .stButton button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        font-family: 'Inter', sans-serif !important;
        height: 36px !important;
    }
    
    .stButton button:hover {
        background: #2563eb !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stButton button:disabled {
        background: #9ca3af !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* API setup */
    .api-setup {
        max-width: 500px;
        margin: 0 auto;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .api-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .api-description {
        color: #6b7280;
        margin-bottom: 1.5rem;
        line-height: 1.5;
        font-size: 0.9rem;
    }
    
    /* Report content */
    .report-content {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        line-height: 1.6;
        color: #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .report-content h1, .report-content h2, .report-content h3 {
        color: #f9fafb;
        margin-top: 1.25rem;
        margin-bottom: 0.625rem;
        font-weight: 600;
    }
    
    .report-content h1 {
        font-size: 1.375rem;
        border-bottom: 2px solid #374151;
        padding-bottom: 0.5rem;
    }
    
    .report-content h2 {
        font-size: 1.125rem;
    }
    
    .report-content h3 {
        font-size: 1rem;
    }
    
    /* Source links styling */
    .report-content a {
        color: #06b6d4 !important;
        text-decoration: none;
    }
    
    .report-content a:hover {
        color: #0891b2 !important;
        text-decoration: underline;
    }
    
    /* Source citations - style [1], [2] etc in dark cyan */
    .assistant-content [1], .assistant-content [2], .assistant-content [3], .assistant-content [4], .assistant-content [5],
    .assistant-content [6], .assistant-content [7], .assistant-content [8], .assistant-content [9], .assistant-content [10] {
        color: #06b6d4;
        font-weight: 500;
    }
    
    .report-content [1], .report-content [2], .report-content [3], .report-content [4], .report-content [5],
    .report-content [6], .report-content [7], .report-content [8], .report-content [9], .report-content [10] {
        color: #06b6d4;
        font-weight: 500;
    }
    
    /* Form styling */
    .stForm {
        border: none !important;
        background: transparent !important;
    }
    
    /* Analyst feedback form */
    .stTextArea textarea[aria-label*="feedback"] {
        background: #374151 !important;
        border: 1px solid #4b5563 !important;
        color: #f9fafb !important;
    }
    
    .stTextArea textarea[aria-label*="feedback"]::placeholder {
        color: #9ca3af !important;
    }
    
    /* Download button styling */
    .stDownloadButton button {
        background: #06b6d4 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        margin: 0.5rem 0 !important;
    }
    
    .stDownloadButton button:hover {
        background: #0891b2 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .chat-area.has-messages {
            padding: 1.5rem 1rem 8rem 1rem;
        }
        
        .chat-area.empty {
            padding: 1rem;
        }
        
        .input-wrapper {
            padding: 0 1rem;
        }
        
        .user-message-content {
            max-width: 85%;
        }
        
        .empty-title {
            font-size: 2rem;
        }
        
        .assistant-content {
            padding: 1rem;
        }
        
        .report-content {
            padding: 1rem;
        }
        
        .assistant-label {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# EXACT MODELS FROM NOTEBOOK (unchanged)
class Analyst(BaseModel):
    affiliation: str = Field(description="Primary affiliation of the analyst.")
    name: str = Field(description="Name of the analyst.")
    role: str = Field(description="Role of the analyst in the context of the topic.")
    description: str = Field(description="Description of the analyst focus, concerns, and motives.")
    
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(description="Comprehensive list of analysts with their roles and affiliations.")

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")

# EXACT STATE DEFINITIONS FROM NOTEBOOK (unchanged)
class GenerateAnalystsState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]

class InterviewState(MessagesState):
    max_num_turns: int
    context: Annotated[list, operator.add]
    analyst: Analyst
    interview: str
    sections: list

class ResearchGraphState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
    sections: Annotated[list, operator.add]
    introduction: str
    content: str
    conclusion: str
    final_report: str

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_keys_set' not in st.session_state:
    st.session_state.api_keys_set = False
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'tavily_search' not in st.session_state:
    st.session_state.tavily_search = None
if 'research_in_progress' not in st.session_state:
    st.session_state.research_in_progress = False
if 'current_analysts' not in st.session_state:
    st.session_state.current_analysts = None
if 'show_analysts' not in st.session_state:
    st.session_state.show_analysts = False
if 'last_report_content' not in st.session_state:
    st.session_state.last_report_content = None
if 'current_thread' not in st.session_state:
    st.session_state.current_thread = None
if 'current_graph' not in st.session_state:
    st.session_state.current_graph = None

def check_api_keys():
    """Check if API keys are available"""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if anthropic_key and tavily_key:
        try:
            st.session_state.api_keys_set = True
            st.session_state.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
            st.session_state.tavily_search = TavilySearch(max_results=3)
            
            # Test the connections
            test_response = st.session_state.llm.invoke([HumanMessage(content="test")])
            return True
        except Exception as e:
            st.session_state.api_keys_set = False
            st.error(f"API Connection failed: {str(e)}")
            return False
    return False

def setup_api_keys():
    """Setup API keys in a clean modal-like interface"""
    st.markdown("""
    <div class="chat-area">
        <div class="api-setup">
            <div class="api-title">API Configuration Required</div>
            <div class="api-description">To get started, please provide your API keys below:</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("api_form"):
        anthropic_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Connect", use_container_width=True)
        
        if submitted:
            if anthropic_key and tavily_key:
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key
                os.environ["TAVILY_API_KEY"] = tavily_key
                if check_api_keys():
                    st.success("Connected successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to connect. Please check your API keys and internet connection.")
            else:
                st.error("Please provide both API keys.")

def add_message(role: str, content: str):
    """Add a message to the chat"""
    st.session_state.messages.append({"role": role, "content": content})

def generate_pdf_weasyprint(content: str, topic: str) -> bytes:
    """Generate PDF using WeasyPrint (HTML to PDF)"""
    try:
        # Clean content and convert markdown-style to HTML
        import html
        content = html.unescape(content)
        content = re.sub(r'\*Research completed.*?\*', '', content, flags=re.DOTALL)
        
        # Convert markdown-style formatting to HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Research Report: {topic}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; }}
                p {{ margin-bottom: 15px; }}
                .sources {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; }}
            </style>
        </head>
        <body>
            <h1>Research Report: {topic}</h1>
        """
        
        # Process content line by line
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line == '---':
                continue
                
            if line.startswith('# '):
                html_content += f"<h1>{line[2:]}</h1>\n"
            elif line.startswith('## '):
                html_content += f"<h2>{line[3:]}</h2>\n"
            elif line.startswith('### '):
                html_content += f"<h3>{line[4:]}</h3>\n"
            elif line.startswith('[') and ']' in line:
                html_content += f'<p class="sources">{line}</p>\n'
            elif line and len(line) > 1:
                html_content += f"<p>{line}</p>\n"
        
        html_content += "</body></html>"
        
        # Generate PDF from HTML
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
        
    except Exception as e:
        print(f"WeasyPrint PDF generation error: {e}")
        raise e

def generate_pdf_reportlab(content: str, topic: str) -> bytes:
    """Generate PDF using ReportLab (fallback)"""
    try:
        if not REPORTLAB_AVAILABLE:
            raise Exception("ReportLab not available")
            
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        story.append(Paragraph(f"Research Report: {topic}", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Process content
        if content and content.strip():
            import html
            content = html.unescape(content)
            content = re.sub(r'\*Research completed.*?\*', '', content, flags=re.DOTALL)
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 1:
                    if line.startswith('# '):
                        story.append(Paragraph(line[2:], styles['Heading1']))
                    elif line.startswith('## '):
                        story.append(Paragraph(line[3:], styles['Heading2']))
                    elif line.startswith('### '):
                        story.append(Paragraph(line[4:], styles['Heading3']))
                    else:
                        story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("No content available for this report.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
        
    except Exception as e:
        print(f"ReportLab PDF generation error: {e}")
        raise e

def generate_pdf(content: str, topic: str) -> bytes:
    """Generate PDF - try WeasyPrint first, fallback to ReportLab"""
    try:
        if WEASYPRINT_AVAILABLE:
            return generate_pdf_weasyprint(content, topic)
        elif REPORTLAB_AVAILABLE:
            return generate_pdf_reportlab(content, topic)
        else:
            # Simple text-based PDF as last resort
            return create_simple_text_pdf(content, topic)
    except Exception as e:
        print(f"All PDF generation methods failed: {e}")
        return create_simple_text_pdf(content, topic)

def create_simple_text_pdf(content: str, topic: str) -> bytes:
    """Create a simple text-based PDF as last resort"""
    try:
        # Use a simple approach to create minimal PDF
        if REPORTLAB_AVAILABLE:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [
                Paragraph(f"Research Report: {topic}", styles['Title']),
                Spacer(1, 20),
                Paragraph("Content preview - full formatting not available", styles['Normal']),
                Spacer(1, 10)
            ]
            
            # Add basic content
            if content:
                clean_content = re.sub(r'<[^>]+>', '', content)  # Remove HTML
                clean_content = re.sub(r'[^\w\s\n\.]', '', clean_content)  # Keep only basic chars
                story.append(Paragraph(clean_content[:1000] + "...", styles['Normal']))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        else:
            # Return minimal PDF bytes if nothing else works
            return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n181\n%%EOF"
    except:
        # Return absolute minimal PDF if everything fails
        return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\nxref\n0 2\ntrailer\n<< /Size 2 /Root 1 0 R >>\nstartxref\n0\n%%EOF"

def create_download_button(pdf_bytes: bytes, filename: str, key: str):
    """Create a Streamlit download button for PDF"""
    return st.download_button(
        label="📄 Download PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        key=key,
        use_container_width=False
    )

def display_messages():
    """Display chat messages in Perplexity style"""
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message user-message">
                <div class="user-message-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check if this is a report message (contains report content)
            is_report = "comprehensive research report" in message["content"] and "report-content" in message["content"]
            
            st.markdown(f"""
            <div class="message assistant-message">
                <div class="assistant-label">
                    <span>Research.ai</span>
                </div>
                <div class="assistant-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add download button below the message if it's a report
            if is_report and hasattr(st.session_state, 'last_report_topic') and st.session_state.last_report_content:
                try:
                    # Use the stored clean content for PDF generation
                    pdf_bytes = generate_pdf(st.session_state.last_report_content, st.session_state.last_report_topic)
                    
                    # Clean filename properly - remove all problematic characters
                    clean_topic = re.sub(r'[^\w\s-]', '', st.session_state.last_report_topic)
                    clean_topic = re.sub(r'\s+', '_', clean_topic)
                    clean_topic = clean_topic.strip('_')[:50]  # Limit length
                    filename = f"research_report_{clean_topic}.pdf"
                    
                    # Create download button
                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col2:
                        create_download_button(pdf_bytes, filename, f"download_pdf_{i}")
                except Exception as e:
                    st.error(f"PDF generation error: {e}")

def display_analysts():
    """Display the research analysts for user review"""
    if st.session_state.current_analysts:
        st.markdown("""
        <div class="message assistant-message">
            <div class="assistant-label">Research.ai - Team Assembly</div>
            <div class="assistant-content">
                <h3>Research Team Assembled</h3>
                <p>I've created a specialized research team for your query. Review the analysts below:</p>
        """, unsafe_allow_html=True)
        
        for i, analyst in enumerate(st.session_state.current_analysts, 1):
            st.markdown(f"""
                <div style="background: #2d3748; border-radius: 8px; padding: 1rem; margin: 0.75rem 0; border-left: 3px solid #06b6d4;">
                    <h4 style="color: #06b6d4; margin: 0 0 0.5rem 0;">{analyst.name}</h4>
                    <p style="margin: 0.25rem 0; color: #a0aec0;"><strong>Role:</strong> {analyst.role}</p>
                    <p style="margin: 0.25rem 0; color: #a0aec0;"><strong>Affiliation:</strong> {analyst.affiliation}</p>
                    <p style="margin: 0.5rem 0 0 0; color: #e2e8f0;">{analyst.description}</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add feedback form
        with st.form("analyst_feedback", clear_on_submit=True):
            feedback = st.text_area(
                "Provide feedback on the research team (optional)",
                placeholder="Any specific focus areas, additional expertise needed, or modifications to the research approach?",
                height=100
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.form_submit_button("Approve Team", use_container_width=True):
                    st.session_state.show_analysts = False
                    continue_research_with_feedback(feedback if feedback else None)
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Regenerate Team", use_container_width=True):
                    # Regenerate with feedback using existing graph and thread
                    if st.session_state.current_graph and st.session_state.current_thread:
                        regenerate_team_with_feedback(feedback if feedback else "")
                    st.rerun()
            
            with col3:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_analysts = False
                    st.session_state.research_in_progress = False
                    st.rerun()

def create_exact_research_graph():
    """Create the EXACT research automation graph from the notebook"""
    
    llm = st.session_state.llm
    tavily_search = st.session_state.tavily_search
    
    # EXACT ANALYST INSTRUCTIONS FROM NOTEBOOK
    analyst_instructions = """You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{topic}

2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts:

{human_analyst_feedback}

3. Determine the most interesting themes based upon documents and / or feedback above.

4. Pick the top {max_analysts} themes.

5. Assign one analyst to each theme."""

    def create_analysts(state: GenerateAnalystsState):
        """Create analysts"""
        topic = state['topic']
        max_analysts = state['max_analysts']
        human_analyst_feedback = state.get('human_analyst_feedback', '')

        # Enforce structured output
        structured_llm = llm.with_structured_output(Perspectives)

        # System message
        system_message = analyst_instructions.format(topic=topic,
                                                               human_analyst_feedback=human_analyst_feedback,
                                                               max_analysts=max_analysts)

        # Generate question
        analysts = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the set of analysts.")])

        # Write the list of analysis to state
        return {"analysts": analysts.analysts}

    def human_feedback(state: GenerateAnalystsState):
        """No-op node that should be interrupted on"""
        pass

    # EXACT QUESTION INSTRUCTIONS FROM NOTEBOOK
    question_instructions = """You are an analyst tasked with interviewing an expert to learn about a specific topic.

Your goal is boil down to interesting and specific insights related to your topic.

1. Interesting: Insights that people will find surprising or non-obvious.

2. Specific: Insights that avoid generalities and include specific examples from the expert.

Here is your topic of focus and set of goals: {goals}

Begin by introducing yourself using a name that fits your persona, and then ask your question.

Continue to ask questions to drill down and refine your understanding of the topic.

When you are satisfied with your understanding, complete the interview with: "Thank you so much for your help!"

Remember to stay in character throughout your response, reflecting the persona and goals provided to you."""

    def generate_question(state: InterviewState):
        """Node to generate a question"""
        # Get state
        analyst = state["analyst"]
        messages = state["messages"]

        # Generate question
        system_message = question_instructions.format(goals=analyst.persona)
        question = llm.invoke([SystemMessage(content=system_message)]+messages)

        # Write messages to state
        return {"messages": [question]}

    # EXACT SEARCH INSTRUCTIONS FROM NOTEBOOK
    search_instructions = SystemMessage(content=f"""You will be given a conversation between an analyst and an expert.

Your goal is to generate a well-structured query for use in retrieval and / or web-search related to the conversation.

First, analyze the full conversation.

Pay particular attention to the final question posed by the analyst.

Convert this final question into a well-structured web search query""")

    def search_web(state: InterviewState):
        """Retrieve docs from web search"""
        # Search query
        structured_llm = llm.with_structured_output(SearchQuery)
        search_query = structured_llm.invoke([search_instructions]+state['messages'])

        # Search
        search_docs = tavily_search.invoke(search_query.search_query)

        # Handle different result formats - fix for TavilySearch
        if isinstance(search_docs, dict) and 'results' in search_docs:
            docs = search_docs['results']
        elif isinstance(search_docs, list):
            docs = search_docs
        else:
            docs = []

        # Format - keep exact same format as notebook
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc.get("url", "unknown")}"/>\n{doc.get("content", doc.get("snippet", "No content"))}\n</Document>'
                for doc in docs if isinstance(doc, dict)
            ]
        )

        return {"context": [formatted_search_docs]}

    def search_wikipedia(state: InterviewState):
        """Retrieve docs from wikipedia"""
        # Search query
        structured_llm = llm.with_structured_output(SearchQuery)
        search_query = structured_llm.invoke([search_instructions]+state['messages'])

        # Search
        search_docs = WikipediaLoader(query=search_query.search_query,
                                      load_max_docs=2).load()

        # Format
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
                for doc in search_docs
            ]
        )

        return {"context": [formatted_search_docs]}

    # EXACT ANSWER INSTRUCTIONS FROM NOTEBOOK
    answer_instructions = """You are an expert being interviewed by an analyst.

Here is analyst area of focus: {goals}.

You goal is to answer a question posed by the interviewer.

To answer question, use this context:

{context}

When answering questions, follow these guidelines:

1. Use only the information provided in the context.

2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.

3. The context contain sources at the topic of each individual document.

4. Include these sources your answer next to any relevant statements. For example, for source # 1 use [1].

5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc

6. If the source is: <Document source="assistant/docs/llama3_1.pdf" page="7"/>' then just list:

[1] assistant/docs/llama3_1.pdf, page 7

And skip the addition of the brackets as well as the Document source preamble in your citation."""

    def generate_answer(state: InterviewState):
        """Node to answer a question"""
        # Get state
        analyst = state["analyst"]
        messages = state["messages"]
        context = state["context"]

        # Answer question
        system_message = answer_instructions.format(goals=analyst.persona, context=context)
        answer = llm.invoke([SystemMessage(content=system_message)]+messages)

        # Name the message as coming from the expert
        answer.name = "expert"

        # Append it to state
        return {"messages": [answer]}

    def save_interview(state: InterviewState):
        """Save interviews"""
        # Get messages
        messages = state["messages"]

        # Convert interview to a string
        interview = get_buffer_string(messages)

        # Save to interviews key
        return {"interview": interview}

    def route_messages(state: InterviewState, name: str = "expert"):
        """Route between question and answer"""
        # Get messages
        messages = state["messages"]
        max_num_turns = state.get('max_num_turns',2)

        # Check the number of expert answers
        num_responses = len(
            [m for m in messages if isinstance(m, AIMessage) and m.name == name]
        )

        # End if expert has answered more than the max turns
        if num_responses >= max_num_turns:
            return 'save_interview'

        # This router is run after each question - answer pair
        # Get the last question asked to check if it signals the end of discussion
        last_question = messages[-2]

        if "Thank you so much for your help" in last_question.content:
            return 'save_interview'
        return "ask_question"

    # EXACT SECTION WRITER INSTRUCTIONS FROM NOTEBOOK
    section_writer_instructions = """You are an expert technical writer.

Your task is to create a short, easily digestible section of a report based on a set of source documents.

1. Analyze the content of the source documents:
- The name of each source document is at the start of the document, with the <Document tag.

2. Create a report structure using markdown formatting:
- Use ## for the section title
- Use ### for sub-section headers

3. Write the report following this structure:
a. Title (## header)
b. Summary (### header)
c. Sources (### header)

4. Make your title engaging based upon the focus area of the analyst:
{focus}

5. For the summary section:
- Set up summary with general background / context related to the focus area of the analyst
- Emphasize what is novel, interesting, or surprising about insights gathered from the interview
- Create a numbered list of source documents, as you use them
- Do not mention the names of interviewers or experts
- Aim for approximately 400 words maximum
- Use numbered sources in your report (e.g., [1], [2]) based on information from source documents

6. In the Sources section:
- Include all sources used in your report
- Provide full links to relevant websites or specific document paths
- Separate each source by a newline. Use two spaces at the end of each line to create a newline in Markdown.
- It will look like:

### Sources
[1] Link or Document name
[2] Link or Document name

7. Be sure to combine sources. For example this is not correct:

[3] https://ai.meta.com/blog/meta-llama-3-1/
[4] https://ai.meta.com/blog/meta-llama-3-1/

There should be no redundant sources. It should simply be:

[3] https://ai.meta.com/blog/meta-llama-3-1/

8. Final review:
- Ensure the report follows the required structure
- Include no preamble before the title of the report
- Check that all guidelines have been followed"""

    def write_section(state: InterviewState):
        """Node to answer a question"""
        # Get state
        interview = state["interview"]
        context = state["context"]
        analyst = state["analyst"]

        # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
        system_message = section_writer_instructions.format(focus=analyst.description)
        section = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Use this source to write your section: {context}")])

        # Append it to state
        return {"sections": [section.content]}

    # EXACT INTERVIEW GRAPH FROM NOTEBOOK
    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node("ask_question", generate_question)
    interview_builder.add_node("search_web", search_web)
    interview_builder.add_node("search_wikipedia", search_wikipedia)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    # Flow
    interview_builder.add_edge(START, "ask_question")
    interview_builder.add_edge("ask_question", "search_web")
    interview_builder.add_edge("ask_question", "search_wikipedia")
    interview_builder.add_edge("search_web", "answer_question")
    interview_builder.add_edge("search_wikipedia", "answer_question")
    interview_builder.add_conditional_edges("answer_question", route_messages,['ask_question','save_interview'])
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)

    # EXACT MAIN GRAPH FUNCTIONS FROM NOTEBOOK
    def initiate_all_interviews(state: ResearchGraphState):
        """This is the "map" step where we run each interview sub-graph using Send API"""
        # Check if human feedback
        human_analyst_feedback=state.get('human_analyst_feedback')
        if human_analyst_feedback:
            # Return to create_analysts
            return "create_analysts"

        # Otherwise kick off interviews in parallel via Send() API
        else:
            topic = state["topic"]
            return [Send("conduct_interview", {"analyst": analyst,
                                               "messages": [HumanMessage(
                                                   content=f"So you said you were writing an article on {topic}?"
                                               )
                                                           ]}) for analyst in state["analysts"]]

    # EXACT REPORT WRITER INSTRUCTIONS FROM NOTEBOOK
    report_writer_instructions = """You are a technical writer creating a report on this overall topic:

{topic}

You have a team of analysts. Each analyst has done two things:

1. They conducted an interview with an expert on a specific sub-topic.
2. They write up their finding into a memo.

Your task:

1. You will be given a collection of memos from your analysts.
2. Think carefully about the insights from each memo.
3. Consolidate these into a crisp overall summary that ties together the central ideas from all of the memos.
4. Summarize the central points in each memo into a cohesive single narrative.

To format your report:

1. Use markdown formatting.
2. Include no pre-amble for the report.
3. Use no sub-heading.
4. Start your report with a single title header: ## Insights
5. Do not mention any analyst names in your report.
6. Preserve any citations in the memos, which will be annotated in brackets, for example [1] or [2].
7. Create a final, consolidated list of sources and add to a Sources section with the `## Sources` header.
8. List your sources in order and do not repeat.

[1] Source 1
[2] Source 2

Here are the memos from your analysts to build your report from:

{context}"""

    def write_report(state: ResearchGraphState):
        # Full set of sections
        sections = state["sections"]
        topic = state["topic"]

        # Concat all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        # Summarize the sections into a final report
        system_message = report_writer_instructions.format(topic=topic, context=formatted_str_sections)
        report = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Write a report based upon these memos.")])
        return {"content": report.content}

    # EXACT INTRO/CONCLUSION INSTRUCTIONS FROM NOTEBOOK
    intro_conclusion_instructions = """You are a technical writer finishing a report on {topic}

You will be given all of the sections of the report.

You job is to write a crisp and compelling introduction or conclusion section.

The user will instruct you whether to write the introduction or conclusion.

Include no pre-amble for either section.

Target around 100 words, crisply previewing (for introduction) or recapping (for conclusion) all of the sections of the report.

Use markdown formatting.

For your introduction, create a compelling title and use the # header for the title.

For your introduction, use ## Introduction as the section header.

For your conclusion, use ## Conclusion as the section header.

Here are the sections to reflect on for writing: {formatted_str_sections}"""

    def write_introduction(state: ResearchGraphState):
        # Full set of sections
        sections = state["sections"]
        topic = state["topic"]

        # Concat all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        # Summarize the sections into a final report
        instructions = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)
        intro = llm.invoke([SystemMessage(content=instructions)]+[HumanMessage(content=f"Write the report introduction")])
        return {"introduction": intro.content}

    def write_conclusion(state: ResearchGraphState):
        # Full set of sections
        sections = state["sections"]
        topic = state["topic"]

        # Concat all sections together
        formatted_str_sections = "\n\n".join([f"{section}" for section in sections])

        # Summarize the sections into a final report
        instructions = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)
        conclusion = llm.invoke([SystemMessage(content=instructions)]+[HumanMessage(content=f"Write the report conclusion")])
        return {"conclusion": conclusion.content}

    def finalize_report(state: ResearchGraphState):
        """The is the "reduce" step where we gather all the sections, combine them, and reflect on them to write the intro/conclusion"""
        # Save full final report
        content = state["content"]
        if content.startswith("## Insights"):
            content = content.strip("## Insights")
        if "## Sources" in content:
            try:
                content, sources = content.split("\n## Sources\n")
            except:
                sources = None
        else:
            sources = None

        final_report = state["introduction"] + "\n\n---\n\n" + content + "\n\n---\n\n" + state["conclusion"]
        if sources is not None:
            final_report += "\n\n## Sources\n" + sources
        return {"final_report": final_report}

    # EXACT GRAPH CONSTRUCTION FROM NOTEBOOK
    builder = StateGraph(ResearchGraphState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)
    builder.add_node("conduct_interview", interview_builder.compile())
    builder.add_node("write_report",write_report)
    builder.add_node("write_introduction",write_introduction)
    builder.add_node("write_conclusion",write_conclusion)
    builder.add_node("finalize_report",finalize_report)

    # EXACT LOGIC FROM NOTEBOOK
    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")
    builder.add_conditional_edges("human_feedback", initiate_all_interviews, ["create_analysts", "conduct_interview"])
    builder.add_edge("conduct_interview", "write_report")
    builder.add_edge("conduct_interview", "write_introduction")
    builder.add_edge("conduct_interview", "write_conclusion")
    builder.add_edge(["write_conclusion", "write_report", "write_introduction"], "finalize_report")
    builder.add_edge("finalize_report", END)

    # Compile
    memory = MemorySaver()
    return builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)

def conduct_research(topic: str):
    """Conduct the research process - first show analysts for approval"""
    st.session_state.research_in_progress = True
    
    try:
        # Validate API connections first
        if not st.session_state.api_keys_set or not st.session_state.llm or not st.session_state.tavily_search:
            add_message("assistant", "API keys not properly configured. Please refresh and set your API keys again.")
            return
        
        # Show progress
        progress_placeholder = st.empty()
        
        with progress_placeholder:
            st.markdown('<div class="progress-message">Initializing AI research analysts...</div>', unsafe_allow_html=True)
        
        # Create graph and start research
        graph = create_exact_research_graph()
        thread = {"configurable": {"thread_id": f"research_{int(time.time())}"}}
        
        # Generate analysts
        result = None
        for event in graph.stream({
            "topic": topic,
            "max_analysts": 3
        }, thread, stream_mode="values"):
            if 'analysts' in event:
                result = event
                break
        
        if not result or 'analysts' not in result:
            add_message("assistant", "Sorry, I encountered an error while setting up the research team. Please check your API keys and try again.")
            return
        
        analysts = result['analysts']
        
        # Store analysts and show them for review
        st.session_state.current_analysts = analysts
        st.session_state.current_thread = thread
        st.session_state.current_graph = graph
        st.session_state.show_analysts = True
        
        # Clear progress
        progress_placeholder.empty()
        
    except Exception as e:
        error_msg = str(e).lower()
        if "connection" in error_msg or "network" in error_msg:
            add_message("assistant", "**Connection Error**: Please check your internet connection and API keys.")
        elif "unauthorized" in error_msg or "403" in error_msg:
            add_message("assistant", "**Authentication Error**: Your API keys appear to be invalid.")
        else:
            add_message("assistant", f"**Research Error**: {str(e)}")
        st.session_state.research_in_progress = False

def continue_research_with_feedback(feedback):
    """Continue the research process after analyst approval"""
    try:
        graph = st.session_state.current_graph
        thread = st.session_state.current_thread
        
        # Show progress
        progress_placeholder = st.empty()
        
        with progress_placeholder:
            st.markdown('<div class="progress-message">Conducting comprehensive multi-agent research...</div>', unsafe_allow_html=True)
        
        # Continue with research using the feedback
        graph.update_state(thread, {"human_analyst_feedback": feedback}, as_node="human_feedback")
        
        # Track progress through nodes
        progress_messages = {
            "conduct_interview": "Conducting expert interviews...",
            "write_report": "Synthesizing findings...",
            "write_introduction": "Crafting introduction...",
            "write_conclusion": "Writing conclusion...",
            "finalize_report": "Finalizing report..."
        }
        
        for event in graph.stream(None, thread, stream_mode="updates"):
            node_name = next(iter(event.keys()))
            if node_name in progress_messages:
                with progress_placeholder:
                    st.markdown(f'<div class="progress-message">{progress_messages[node_name]}</div>', unsafe_allow_html=True)
                time.sleep(0.5)
        
        # Get final result
        final_state = graph.get_state(thread)
        
        # Clear progress
        progress_placeholder.empty()
        
        if 'final_report' in final_state.values:
            report = final_state.values['final_report']
            
            # Store the clean report content for PDF generation
            st.session_state.last_report_content = report
            
            # Add report to chat
            add_message("assistant", f"""Here's your comprehensive research report on **{st.session_state.last_report_topic}**:

<div class="report-content">

{report}

</div>

*Research completed using multi-agent AI analysis with real-time web search and expert knowledge synthesis.*
""")
        else:
            add_message("assistant", "I encountered an issue while generating the final report. Please try again.")
    
    except Exception as e:
        add_message("assistant", f"**Research Error**: {str(e)}")
    
    finally:
        st.session_state.research_in_progress = False

def create_analyst_feedback_graph():
    """Create a separate graph just for analyst generation with feedback (following notebook pattern)"""
    llm = st.session_state.llm
    
    # EXACT ANALYST INSTRUCTIONS FROM NOTEBOOK
    analyst_instructions = """You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{topic}

2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts:

{human_analyst_feedback}

3. Determine the most interesting themes based upon documents and / or feedback above.

4. Pick the top {max_analysts} themes.

5. Assign one analyst to each theme."""

    def create_analysts(state: GenerateAnalystsState):
        """Create analysts"""
        topic = state['topic']
        max_analysts = state['max_analysts']
        human_analyst_feedback = state.get('human_analyst_feedback', '')

        # Enforce structured output
        structured_llm = llm.with_structured_output(Perspectives)

        # System message
        system_message = analyst_instructions.format(topic=topic,
                                                    human_analyst_feedback=human_analyst_feedback,
                                                    max_analysts=max_analysts)

        # Generate analysts
        analysts = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the set of analysts.")])

        # Write the list of analysts to state
        return {"analysts": analysts.analysts}

    def human_feedback(state: GenerateAnalystsState):
        """No-op node that should be interrupted on"""
        pass

    def should_continue(state: GenerateAnalystsState):
        """Return the next node to execute (exact notebook pattern)"""
        # Check if human feedback
        human_analyst_feedback = state.get('human_analyst_feedback', None)
        if human_analyst_feedback:
            return "create_analysts"
        # Otherwise end
        return END

    # Build the graph exactly like the notebook
    builder = StateGraph(GenerateAnalystsState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)
    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")
    builder.add_conditional_edges("human_feedback", should_continue, ["create_analysts", END])

    # Compile with checkpointer
    memory = MemorySaver()
    return builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)

def regenerate_team_with_feedback(feedback: str):
    """Regenerate analysts with human feedback using the exact notebook pattern"""
    try:
        # Show progress
        progress_placeholder = st.empty()
        with progress_placeholder:
            st.markdown('<div class="progress-message">Regenerating research team with your feedback...</div>', unsafe_allow_html=True)
        
        # Create the feedback graph (like in notebook)
        feedback_graph = create_analyst_feedback_graph()
        feedback_thread = {"configurable": {"thread_id": f"feedback_{int(time.time())}"}}
        
        # Get current topic
        topic = st.session_state.last_report_topic
        
        # First run - generate initial analysts
        initial_result = None
        for event in feedback_graph.stream({
            "topic": topic,
            "max_analysts": 3
        }, feedback_thread, stream_mode="values"):
            if 'analysts' in event:
                initial_result = event
                break
        
        # Update with feedback (exact notebook pattern)
        feedback_graph.update_state(feedback_thread, {"human_analyst_feedback": feedback}, as_node="human_feedback")
        
        # Continue execution with feedback
        final_result = None
        for event in feedback_graph.stream(None, feedback_thread, stream_mode="values"):
            if 'analysts' in event:
                final_result = event
                # Don't break - get the last one (most recent)
        
        # Clear progress
        progress_placeholder.empty()
        
        if final_result and 'analysts' in final_result:
            # Update the analysts with the new feedback-influenced team
            st.session_state.current_analysts = final_result['analysts']
            st.session_state.show_analysts = True
            
            # Update the main graph's state too
            if st.session_state.current_graph and st.session_state.current_thread:
                st.session_state.current_graph.update_state(
                    st.session_state.current_thread, 
                    {"analysts": final_result['analysts']}, 
                    as_node="create_analysts"
                )
            
            # Show success message
            st.success(f"✅ Team regenerated successfully with {len(final_result['analysts'])} analysts!")
        else:
            st.error("Failed to regenerate analysts with feedback")
            
    except Exception as e:
        if 'progress_placeholder' in locals():
            progress_placeholder.empty()
        st.error(f"Error regenerating team with feedback: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def generate_new_analysts(topic: str):
    """Generate new analysts directly"""
    try:
        # Create graph and generate new analysts
        graph = create_exact_research_graph()
        
        # Generate fresh analysts
        result = None
        for event in graph.stream({
            "topic": topic,
            "max_analysts": 3
        }, {"configurable": {"thread_id": f"regen_{int(time.time())}"}}, stream_mode="values"):
            if 'analysts' in event:
                result = event
                break
        
        if result and 'analysts' in result:
            # Update the analysts directly
            st.session_state.current_analysts = result['analysts']
            st.session_state.show_analysts = True
        else:
            st.error("Failed to generate new analysts")
            
    except Exception as e:
        st.error(f"Error generating new analysts: {e}")

def regenerate_analysts():
    """Regenerate the research analysts"""
    if st.session_state.last_report_topic:
        # Clear current analysts first
        st.session_state.current_analysts = None
        st.session_state.show_analysts = False
        
        # Start fresh research process
        conduct_research(st.session_state.last_report_topic)

def main():
    # Check API keys on startup
    check_api_keys()
    
    # Main content area
    if not st.session_state.api_keys_set:
        setup_api_keys()
        return
    
    # Determine if we have messages for layout
    has_messages = len(st.session_state.messages) > 0
    chat_class = "has-messages" if has_messages else "empty"
    input_class = "has-messages" if has_messages else "empty"
    
    # Main chat area
    st.markdown(f'<div class="chat-area {chat_class}">', unsafe_allow_html=True)
    
    # Empty state or messages
    if not has_messages:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-title">Research.ai</div>
            <div class="empty-subtitle">Your AI-powered research assistant</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        display_messages()
        
        # Show analysts for review if needed
        if st.session_state.show_analysts:
            display_analysts()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input container - centered when empty, fixed when has messages
    st.markdown(f"""
    <div class="input-container {input_class}">
        <div class="input-wrapper">
    """, unsafe_allow_html=True)
    
    # Input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([10, 1])
        
        with col1:
            user_input = st.text_area(
                "research_input",
                placeholder="Ask me to research anything...",
                height=68,
                label_visibility="collapsed",
                disabled=st.session_state.research_in_progress
            )
        
        with col2:
            st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
            submit = st.form_submit_button(
                "Research" if not st.session_state.research_in_progress else "Working...",
                disabled=st.session_state.research_in_progress,
                use_container_width=True
            )
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle form submission
    if submit and user_input and not st.session_state.research_in_progress:
        # Store the topic for PDF generation
        st.session_state.last_report_topic = user_input
        
        # Add user message
        add_message("user", user_input)
        
        # Start research
        conduct_research(user_input)
        
        # Rerun to show new messages
        st.rerun()

if __name__ == "__main__":
    main() 