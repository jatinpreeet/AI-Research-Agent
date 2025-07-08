# 🔍 AI Research Agent - Perplexity-Style Browser

A powerful multi-agent research automation system built with LangGraph that creates specialized AI analysts to conduct comprehensive research on any topic.

## ✨ Features

- **🤖 Multi-Agent Analysis**: Automatically generates specialized AI analysts for different perspectives
- **👥 Human-in-the-Loop**: Provide feedback to customize analyst selection  
- **🔄 Map-Reduce Architecture**: Parallel research execution using LangGraph's Send API
- **🌐 Real-time Web Search**: Integration with Tavily for current information
- **📊 Comprehensive Reports**: Generates detailed reports with introduction, insights, and conclusion
- **🎨 Beautiful UI**: Perplexity-style interface built with Streamlit

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

### 3. Setup API Keys

In the sidebar, enter:
- **Anthropic API Key** (for Claude)
- **Tavily API Key** (for web search)

### 4. Start Researching!

1. Enter your research topic
2. Choose number of analysts (2-5)
3. Review generated analysts
4. Provide feedback (optional)
5. Get your comprehensive report

## 🏗️ Architecture

### Based on Cell 43 from Multi_agent_ResearchAutomation.ipynb

This implementation uses the complete map-reduce pattern:

1. **Map Phase**: Multiple AI analysts conduct parallel interviews with experts
2. **Reduce Phase**: Results are combined into a coherent final report

### Key Components

- **Analyst Generation**: Creates specialized AI personas
- **Interview Process**: Each analyst conducts structured expert interviews
- **Web Search Integration**: Real-time information gathering
- **Report Synthesis**: Combines insights into final report

## 📁 Files

- `app.py` - Simplified version
- `app_complete.py` - Full implementation with complete interview process
- `requirements.txt` - Dependencies
- `Multi_agent_ResearchAutomation.ipynb` - Original notebook

## 🎯 Example Topics

Try researching:
- "Future of AI in education"
- "Impact of remote work on productivity" 
- "Sustainable energy solutions for 2024"
- "Effects of social media on mental health"
- "Cryptocurrency adoption trends"

## 🔧 Technical Details

### Built With
- **LangGraph**: State machine orchestration
- **LangChain**: LLM integration
- **Streamlit**: Web interface
- **Claude**: AI reasoning
- **Tavily**: Web search

### Map-Reduce Implementation
Uses LangGraph's `Send` API to run analyst interviews in parallel, then combines results into a final report with introduction, insights, and conclusion.

## 🚨 API Requirements

You'll need API keys from:
1. [Anthropic](https://console.anthropic.com/) - For Claude AI
2. [Tavily](https://tavily.com/) - For web search

## 🎨 UI Features

- **Modern Design**: Gradient headers and card layouts
- **Real-time Progress**: Progress bars during research
- **Responsive Layout**: Works on desktop and mobile
- **Download Reports**: Export as markdown files

## 🔄 Workflow

1. **Topic Input** → AI generates specialized analysts
2. **Human Feedback** → Refine analyst selection (optional)
3. **Parallel Research** → Each analyst conducts expert interviews
4. **Report Generation** → Combine insights into final report
5. **Export** → Download as markdown file

## 🤝 Contributing

This is based on the LangGraph multi-agent research pattern. Feel free to:
- Add new search providers
- Enhance the UI
- Add new analyst types
- Improve report formatting

## 📄 License

Open source - feel free to use and modify!

---

**Built with ❤️ using LangGraph and Streamlit** 