# AI Research Agent

A sophisticated multi-agent research automation platform that leverages AI to conduct comprehensive research on any topic. The system generates specialized research teams, conducts expert interviews, and produces detailed analytical reports.

## What Does This Do?

Imagine having a team of expert researchers at your disposal who can investigate any topic in minutes. This AI Research Agent:

1. **Analyzes your research topic** and automatically creates a team of specialized AI analysts (e.g., a technology expert, policy researcher, and industry analyst)
2. **Each AI analyst conducts structured interviews** with simulated domain experts to gather insights
3. **Searches the web in real-time** using Tavily API to find current, relevant information
4. **Synthesizes all findings** into a comprehensive research report with proper citations
5. **Generates professional PDF reports** that you can download and share

## How It Works

### Step 1: Topic Analysis & Team Generation
When you enter a research topic like "Impact of AI on Healthcare," the system:
- Analyzes the topic complexity and scope
- Generates 3 specialized AI analysts with distinct expertise areas
- Each analyst has a unique perspective, affiliation, and research focus

### Step 2: Human Review & Feedback
- You review the proposed research team
- Provide feedback to adjust expertise areas (e.g., "Add a patient advocacy perspective")
- Regenerate the team with your feedback incorporated

### Step 3: Automated Research Execution
- Each analyst conducts structured interviews with AI experts
- Real-time web searches gather current information and data
- Wikipedia integration provides foundational knowledge
- All sources are tracked and cited properly

### Step 4: Report Generation
- Individual analyst findings are synthesized into coherent sections
- A comprehensive report is generated with introduction, insights, and conclusion
- Professional PDF formatting with proper citations and sources

## Key Features

- **Dynamic Research Team Generation**: Creates specialized AI analyst personas based on research topics
- **Human Feedback Integration**: Interactive team review and regeneration with custom feedback
- **Multi-Source Information Gathering**: Integrates Tavily web search and Wikipedia APIs
- **Automated Expert Interviews**: AI analysts conduct structured interviews to gather insights
- **Comprehensive Report Generation**: Produces detailed reports with citations and sources
- **PDF Export Functionality**: Generates professional PDF reports with multiple formatting options
- **Real-time Progress Tracking**: Live updates during research execution

## Technical Stack

- **Framework**: Streamlit for web interface
- **AI Orchestration**: LangGraph for multi-agent workflow management
- **Language Model**: Anthropic Claude integration
- **Search Integration**: Tavily API and Wikipedia API
- **State Management**: LangGraph checkpointing and memory
- **Report Generation**: WeasyPrint and ReportLab for PDF creation
- **Architecture**: Event-driven state graph with conditional routing

## Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- Git installed on your system

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone this repository

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get API Keys

You need two API keys to run this application:

1). Anthropic API Key (for Claude AI)

2). Tavily API Key (for Web Search)

### Step 3: Run the Application

```bash
# Start the Streamlit application
streamlit run app_exact.py
```

### Step 5: Start Researching!

1. **Enter Research Topic**: Type any topic you want to research (e.g., "Future of renewable energy")
2. **Review Research Team**: The AI will generate 3 specialized analysts
3. **Provide Feedback** (Optional): 
   - Add feedback like "Include an environmental policy expert"
   - Click "Regenerate Team" to update the analysts
4. **Approve Team**: Click "Approve Team" to start the research
5. **Wait for Research**: Watch as each analyst conducts interviews and gathers information
6. **Download Report**: Get your comprehensive PDF report

## Example Research Topics

Try these topics to see the system in action:
- "Impact of AI on job markets in 2024"
- "Sustainable urban planning strategies"
- "Cybersecurity trends for small businesses"
- "Mental health effects of remote work"
- "Future of electric vehicle adoption"

## What Happens During Research?

When you approve a research team, here's what happens behind the scenes:

1. **Parallel Research Execution**: Each analyst works simultaneously
2. **Expert Interviews**: AI analysts conduct structured conversations with domain experts
3. **Web Search**: Real-time searches for current data and trends
4. **Information Synthesis**: Findings are organized and cross-referenced
5. **Report Generation**: All insights are combined into a professional report
6. **Quality Assurance**: Citations are verified and sources are properly attributed

The entire process typically takes 2-5 minutes depending on topic complexity.

## Architecture

The system implements a sophisticated map-reduce pattern for multi-agent research:

### Map Phase
- Multiple specialized AI analysts are generated based on the research topic
- Each analyst conducts structured expert interviews in parallel
- Real-time web search and knowledge base queries gather current information

### Reduce Phase
- Individual analyst findings are synthesized into coherent sections
- A comprehensive report is generated with introduction, insights, and conclusion
- Citations and sources are properly formatted and included

### State Management
- LangGraph manages complex workflow states and checkpoints
- Human feedback loops allow for dynamic team regeneration
- Conditional routing handles various research scenarios


## Project Structure

```
AI-Research-Agent/
├── app_exact.py              # Main Streamlit application
├── Multi_agent_ResearchAutomation.ipynb  # Original research notebook
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

## Report Output

Generated reports include:
- **Executive Summary**: Key findings and insights overview
- **Detailed Analysis Sections**: Individual perspectives from each specialist analyst
- **Comprehensive Source Citations**: Properly formatted references and links
- **Professional PDF Formatting**: Clean, readable layout suitable for sharing
- **Multiple Download Formats**: PDF primary, with potential for other formats


This project is open source and available under standard licensing terms.

## Technical Implementation Details

### Core Technologies
- **LangGraph**: Manages complex multi-agent workflows with state persistence
- **Streamlit**: Provides responsive web interface with real-time updates  
- **Anthropic Claude**: Powers AI reasoning, analysis, and report generation
- **Tavily API**: Enables real-time web search with source attribution
- **Wikipedia API**: Provides foundational knowledge and background information

### Architecture Highlights
- **Event-Driven State Management**: Each research step updates global state
- **Parallel Processing**: Multiple analysts work simultaneously using async patterns
- **Human-in-the-Loop**: Interactive feedback loops for team customization
- **Error Resilience**: Graceful handling of API failures and network issues
- **Citation Tracking**: Automatic source attribution throughout the research process