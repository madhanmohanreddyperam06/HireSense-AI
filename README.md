# 🤖 HireSense AI - AI-Powered Resume Intelligence & Ranking System

An intelligent recruitment automation tool that ranks resumes against job descriptions using BERT embeddings, skill ontology mapping, bias detection, and explainable AI.

## 🎯 Features

- **🤖 BERT-based Semantic Analysis**: Uses `all-MiniLM-L6-v2` model for accurate text similarity
- **🧠 Skill Ontology Mapping**: Comprehensive skill categorization with 10+ categories
- **⚖️ Bias Detection**: Identifies potential bias in resumes and job descriptions
- **🔍 Explainable AI**: Detailed explanations for ranking decisions
- **📊 Interactive Visualizations**: Rich charts and graphs with Plotly
- **🔄 Multi-candidate Comparison**: Side-by-side candidate analysis
- **📱 Modern UI**: Clean, responsive Streamlit interface

## 🏗️ System Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Resume Upload │───▶│  Text Extraction │───▶│  NLP Processing │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐     ┌──────────────────┐          ▼
│ Job Description │───▶│  BERT Embeddings │    ┌─────────────────┐
│   Analysis      │     └──────────────────┘    │  Scoring Engine │
└─────────────────┘                             └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐          ▼
│  Bias Detection │    │  Skill Mapping   │    ┌─────────────────┐
│                 │    │                  │    │  Ranking &      │
│                 │    │                  │    │  Visualization  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend

- **Python 3.10+**
- **sentence-transformers**: BERT embeddings
- **scikit-learn**: Machine learning utilities
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **spaCy**: NLP preprocessing
- **pdfplumber**: PDF text extraction
- **python-docx**: DOCX text extraction
- **textstat**: Readability analysis

### Frontend

- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations

## 📦 Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd "AI Powered Resume Ranking Tool"
```

1. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Download spaCy model**

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### How to Use

1. **Start at Home Page**: Read the overview and system capabilities
2. **Upload Job Description**: Navigate to "Upload Resumes" and paste the job description
3. **Upload Resumes**: Add candidate resumes (PDF/DOCX format)
4. **View Rankings**: Check the "Ranking Dashboard" for AI-powered rankings
5. **Analyze Results**: Explore candidate insights, bias analysis, and comparisons

### Supported File Formats

- **PDF**: `.pdf` files
- **Microsoft Word**: `.docx` files

## 📊 Scoring Formula

The system uses a weighted scoring model:

```text
Final Score = (0.6 × Semantic Similarity) 
            + (0.25 × Skill Match %) 
            + (0.1 × Experience Score) 
            + (0.05 × Education Relevance)
```

### Score Components

1. **Semantic Similarity (60%)**: BERT-based text similarity between resume and job description
2. **Skill Match (25%)**: Coverage of required skills based on ontology mapping
3. **Experience Score (10%)**: Alignment with experience requirements
4. **Education Relevance (5%)**: Match with education requirements

## 🧠 Skill Ontology

The system includes 10 skill categories:

- **Programming**: Python, Java, C++, JavaScript, etc.
- **Machine Learning**: TensorFlow, PyTorch, scikit-learn, etc.
- **Web Development**: React, Django, Flask, Node.js, etc.
- **Databases**: MySQL, PostgreSQL, MongoDB, etc.
- **Cloud & DevOps**: AWS, Docker, Kubernetes, etc.
- **Data Engineering**: Spark, Hadoop, Kafka, etc.
- **Mobile Development**: React Native, Flutter, iOS, Android
- **Cybersecurity**: Network security, cryptography, SIEM
- **Project Management**: Agile, Scrum, JIRA, Confluence
- **Soft Skills**: Communication, leadership, teamwork

## ⚖️ Bias Detection

The system detects and flags:

### Types of Bias

- **Gender Indicators**: Pronouns, gender-coded language
- **Age Indicators**: Age-related terms, experience requirements
- **Personal Attributes**: Marital status, family information
- **Unnecessary Information**: Physical attributes, photos

### Bias Risk Levels

- **Low (0-33)**: Minimal bias detected
- **Medium (34-66)**: Some bias indicators present
- **High (67-100)**: Significant bias detected

### Recommendations

- **For Resumes**: Remove personal information, focus on professional qualifications
- **For Job Descriptions**: Use inclusive language, avoid discriminatory requirements

## 📈 Visualizations

### Available Charts

- **Ranking Bar Chart**: Horizontal bar chart of candidate rankings
- **Skill Radar Chart**: Spider chart comparing job requirements vs candidate skills
- **Score Breakdown**: Stacked bar chart showing score components
- **Bias Risk Gauge**: Speedometer-style gauge for bias assessment
- **Similarity Heatmap**: Heat map of semantic similarities
- **Candidate Comparison**: Side-by-side comparison charts
- **Experience Distribution**: Histogram of candidate experience

## 🔍 Explainable AI

The system provides comprehensive explanations for every ranking decision using multiple AI explainability techniques:

### Why a Candidate Ranked Higher

#### **Semantic Analysis Breakdown**

- **BERT Similarity Score**: Exact percentage match between resume and job description
- **Key Phrase Matches**: Specific terms that contributed to similarity
- **Context Relevance**: How well experience aligns with role requirements
- **Industry Alignment**: Matching of industry-specific terminology

#### **Skill Assessment Details**

- **Strong Skill Categories**: Categories with 80%+ match rate
- **Matched Required Skills**: Exact skills that fulfilled job requirements
- **Skill Gap Analysis**: Missing skills and their impact on ranking
- **Skill Weight Impact**: How each skill category affected final score

#### **Experience & Education Analysis**

- **Experience Alignment**: Years of experience vs. requirements
- **Relevance Scoring**: How relevant the experience is to the role
- **Education Match**: Degree relevance to field requirements
- **Certification Impact**: Professional certifications and their value

### Score Breakdown & Transparency

#### **Component Contributions**

- **Individual Component Scores**: Detailed breakdown of each scoring factor
- **Weight Contributions**: How each weighted component affects final score
- **Normalization Process**: How raw scores are normalized to 0-100 scale
- **Ranking Algorithm**: Step-by-step explanation of ranking logic

#### **Comparative Analysis**

- **Peer Comparison**: How candidate scores against others
- **Strength Areas**: Top-performing categories for each candidate
- **Improvement Opportunities**: Specific areas for enhancement
- **Decision Factors**: Key reasons for ranking position

### Explainability Features

#### **Interactive Explanations**

- **Hover Details**: Additional information on hover over scores
- **Drill-down Capability**: Click to explore detailed breakdowns
- **Visual Indicators**: Color-coded strengths and weaknesses
- **Progressive Disclosure**: Layered information access

#### **Bias-Aware Explanations**

- **Bias Impact Assessment**: How detected bias affected rankings
- **Fairness Metrics**: Explanation of bias mitigation
- **Objective Criteria**: Focus on professional qualifications
- **Transparency Reports**: Full audit trail of decisions

### Technical Implementation

#### **Explainability Engine**

- **SHAP Values**: Feature importance for ML models
- **Attention Visualization**: BERT attention weights for text matching
- **Rule-based Explanations**: Clear logic for scoring rules
- **Hybrid Approach**: Combining ML and rule-based transparency

#### **User-Friendly Format**

- **Natural Language**: Plain English explanations
- **Actionable Insights**: Specific recommendations for improvement
- **Visual Aids**: Charts and graphs for better understanding
- **Multi-level Detail**: Summary to detailed explanations

## 📁 Project Structure

```text
AI Powered Resume Ranking Tool/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── src/                           # Source code modules
│   ├── __init__.py               # Package initialization
│   ├── embedding_engine.py       # BERT embedding functionality
│   ├── text_extractor.py         # PDF/DOCX text extraction
│   ├── skill_mapper.py           # Skill ontology mapping
│   ├── bias_detector.py          # Bias detection system
│   ├── explainability_engine.py  # Explainable AI layer
│   ├── scoring_engine.py         # Main scoring and ranking
│   └── visualization.py          # Chart creation utilities
├── data/                          # Data files
│   └── skill_ontology.json       # Skill categories and definitions
├── examples/                      # Example resumes (optional)
└── tests/                         # Test files (optional)
```

## ⚙️ Configuration

### Scoring Weights

Weights can be adjusted in the sidebar:

- Semantic Similarity: 0.0 - 1.0
- Skill Match: 0.0 - 1.0
- Experience Score: 0.0 - 1.0
- Education Relevance: 0.0 - 1.0

#### Note

Weights must sum to 1.0

### Skill Ontology

Customize `data/skill_ontology.json` to:

- Add new skill categories
- Modify existing skills
- Update category weights

## 🧪 Testing

### Example Usage

```python
from src.scoring_engine import ScoringEngine
from src.text_extractor import TextExtractor

# Initialize engines
scoring_engine = ScoringEngine()
text_extractor = TextExtractor()

# Analyze job description
job_analysis = scoring_engine.analyze_job_description(job_text)

# Extract and analyze resume
resume_text = text_extractor.extract_text_from_file(file_content, filename)
candidate = scoring_engine.analyze_resume(resume_text, filename, job_analysis)
```

## 🚀 Production Considerations

### Performance Optimization

- **Model Caching**: BERT model cached with Streamlit
- **Batch Processing**: Multiple resumes processed efficiently
- **Lazy Loading**: Components loaded on-demand

### Security

- **File Validation**: Only PDF/DOCX files accepted
- **Text Sanitization**: Input text cleaned and validated
- **No Persistent Storage**: Data processed in memory only

### Scalability

- **Modular Architecture**: Easy to extend and modify
- **Component-based**: Independent modules for maintenance
- **Configuration-driven**: Weights and ontology easily updated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

#### Model Loading Error

```bash
# Ensure stable internet connection for first-time model download
pip install --upgrade sentence-transformers
```

#### PDF Extraction Issues

```bash
# Install additional dependencies if needed
pip install pdfplumber
```

#### Memory Issues

```bash
# Reduce batch size in embedding_engine.py if needed
# Or process fewer resumes at once
```

#### spaCy Model Not Found

```bash
python -m spacy download en_core_web_sm
```

### Performance Tips

- Process resumes in batches of 10 or fewer
- Use SSD for better I/O performance
- Ensure sufficient RAM (8GB+ recommended)

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the code documentation
3. Create an issue in the repository

---

### Built with ❤️ for ethical and transparent AI recruitment
