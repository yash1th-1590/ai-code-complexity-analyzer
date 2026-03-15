from flask import Flask, render_template, request, jsonify
import requests
import re
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
# API configuration
HF_API_KEY = os.getenv("HF_API_KEY", os.getenv("HF_TOKEN"))
API_URL = "https://router.huggingface.co/v1/chat/completions"


# ---------------------------
# Clean AI Output
# ---------------------------
def clean_ai_output(ai_text):

    # Remove markdown formatting
    ai_text = ai_text.replace("```python", "").replace("```", "")
    ai_text = ai_text.replace("**", "")

    # Remove repeated prompt rules if AI echoes them
    ai_text = re.sub(r'Rules:.*?Code to analyze:', '', ai_text, flags=re.DOTALL)

    # Remove unnecessary "However" sentences
    lines = ai_text.split("\n")
    cleaned_lines = [line for line in lines if not line.strip().startswith("However")]

    return "\n".join(cleaned_lines).strip()


# ---------------------------
# Ask AI for Code Review
# ---------------------------
def ask_ai(code):

    prompt = f"""
You are an expert programming assistant.

Analyze the given Python code carefully.

Rules:
1. Identify the algorithm used in the code.
2. Provide the time complexity in Big-O notation.
3. Suggest at least two improvements.
4. The optimized code must keep the SAME functionality and logic.
5. The optimized code should improve readability, performance, or structure.

STRICT RULES (MANDATORY):
• The optimized code MUST use the EXACT SAME algorithm used in the original code.
• You are ONLY allowed to improve code structure, readability, robustness, or minor performance aspects.
• You MUST NOT replace the algorithm with a different one.
• DO NOT convert the algorithm into a different approach (example: linear search → hash table, bubble sort → merge sort).
• The algorithmic steps and logic must remain the same.

Optimization Guidelines:
• Improvements may include better variable names or clearer structure.
• Improvements may also include removing redundant operations, improving loop structure, or simplifying conditions.
• Improvements should make the code more readable, efficient, and robust for general cases.
• The optimization should not focus only on formatting or documentation.
• Consider improvements in logic clarity, efficiency, and robustness whenever possible.
Optimization Behavior:
• Improvements should depend on the given code and should not follow a fixed pattern.
• Do not always add docstrings or rename variables if they are already clear.
• Apply improvements only when they meaningfully improve the code.
• Possible improvements may include readability, performance, robustness, or minor error handling where appropriate.
• Choose only the improvements that best suit the given code instead of applying all improvements every time.

Response Format (follow strictly):

Algorithm:
Explain the algorithm in one clear sentence.

Time Complexity:
Provide the Big-O complexity.

Suggestions:
1. First improvement suggestion
2. Second improvement suggestion
No need to specify the side heading as first and second improvement sujjestion.

Optimization Type:
It should clearly explain the changes made in the given code to achieve the optimized code.It should give a detailed explanation about the changes in 2 or 3 lines.

Optimized Code:
Write the FULL optimized working code.

Only output the final optimized code.
Do not include explanations inside the code block.

Alternative Algorithms:
List a maximum of 3 alternatives (or fewer if not applicable).
Give the correct and strictly relevant algorithm names.
The alternative algorithms should be better than the one used in the given code.

Strict Format:
Algorithm Name - Complexity - One-line description

Rules for description:
• The description MUST be only one short line.
• Maximum 12–15 words.
• Do NOT write multiple sentences.
• Do NOT add extra explanations.

Example:
Binary Search - O(log n) - Efficient searching in sorted arrays.
Merge Sort - O(n log n) - Stable divide-and-conquer sorting algorithm.

Why Optimized Code is Better:
Explain clearly what improvements were made compared to the original code.

Code to analyze:
{code}
"""

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.2
    }

    try:

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        result = response.json()

        if "choices" in result:
            ai_text = result["choices"][0]["message"]["content"]
            return clean_ai_output(ai_text)

        if "error" in result:
            return "AI Error: " + str(result["error"])

        return str(result)

    except Exception as e:
        return "AI Error: " + str(e)


# ---------------------------
# Home Page
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------
# Code Analysis API
# ---------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    code = request.json.get("code", "")

    # Static Code Analysis
    total_lines = len(code.split("\n"))
    loops = len(re.findall(r'\b(for|while)\b', code))
    conditions = len(re.findall(r'\bif\b', code))
    functions = len(re.findall(r'\bdef\b', code))

    analysis = f"""
Total Lines: {total_lines}
Loops: {loops}
Conditions: {conditions}
Functions: {functions}
"""

    # AI Code Review
    ai_result = ask_ai(code)

    return jsonify({
        "analysis": analysis.strip(),
        "ai": ai_result
    })


# ---------------------------
# Run Server
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)