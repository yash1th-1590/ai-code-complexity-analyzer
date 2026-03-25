# AI Code Complexity Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-API-yellow.svg)](https://huggingface.co/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

An intelligent web application that analyzes Python code for algorithmic complexity, provides AI-powered code reviews, and suggests optimizations while preserving the original algorithm logic.



## 🚀 Features

### 📊 Static Code Analysis
- **Line Count**: Total lines of code
- **Loop Detection**: Identifies `for` and `while` loops
- **Conditional Statements**: Counts `if` statements
- **Function Definitions**: Detects `def` keywords

### 🤖 AI-Powered Code Review
- **Algorithm Identification**: Detects the algorithm used in the code
- **Time Complexity Analysis**: Provides Big-O notation for algorithmic complexity
- **Smart Suggestions**: Offers two meaningful improvements
- **Optimization Type**: Explains the changes made for optimization
- **Optimized Code**: Generates improved code preserving the same algorithm
- **Alternative Algorithms**: Suggests better algorithms with complexity and descriptions
- **Optimization Justification**: Explains why the optimized code is better

### 🎨 Modern UI Features
- **Dark/Light Theme Toggle**: Personalize your viewing experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Code Syntax Highlighting**: Clean display of code blocks
- **Structured Results**: Organized sections for easy reading
- **Copy-Ready Code**: Easy to copy optimized code snippets

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** - Core programming language
- **Flask** - Web framework
- **Requests** - API calls to Hugging Face
- **Regex** - Pattern matching for static analysis
- **python-dotenv** - Environment variable management

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with dark/light theme support
- **JavaScript (ES6)** - Dynamic interactions and API integration
- **Font Awesome** - Icons and visual elements
- **Google Fonts (Inter)** - Modern typography

### AI Integration
- **Hugging Face API** - Llama 3.1 8B Instruct model for code analysis

## 📋 Prerequisites

- Python 3.8 or higher
- Hugging Face API key ([Get one here](https://huggingface.co/settings/tokens))
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yash1th-1590/ai-code-complexity-analyzer.git
cd ai-code-complexity-analyzer
