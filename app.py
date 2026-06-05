from flask import Flask, render_template, request, jsonify
import requests
import re
import ast
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://router.huggingface.co/v1/chat/completions"

MAX_LINES = 200
MAX_CHARS = 10000


def clean_ai_output(ai_text):
    ai_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', ai_text)
    first_tag = re.search(r'\[ALGORITHM\]', ai_text, re.IGNORECASE)
    if first_tag:
        ai_text = ai_text[first_tag.start():]
    ai_text = ai_text.strip()
    return ai_text


def get_nesting_depth(node, current_depth=0):
    loop_types = (ast.For, ast.While)
    depths = [current_depth]
    for child in ast.iter_child_nodes(node):
        extra = 1 if isinstance(child, loop_types) else 0
        depths.append(get_nesting_depth(child, current_depth + extra))
    return max(depths)


def analyze_code_ast(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"error": f"Syntax error in code: {e}"}

    lines = code.split("\n")
    total_lines = len(lines)
    blank_lines = sum(1 for l in lines if l.strip() == "")
    comment_lines = sum(1 for l in lines if l.strip().startswith("#"))

    loops = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While)))
    conditions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.If))
    functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    list_comps = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ListComp))
    lambdas = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Lambda))
    imports = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))

    max_nesting = get_nesting_depth(tree)

    function_nesting = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            depth = get_nesting_depth(node)
            function_nesting.append({"name": node.name, "depth": depth, "line": node.lineno})

    nesting_per_line = []
    depth = 0
    indent_stack = [0]
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            nesting_per_line.append(depth)
            continue
        indent = len(line) - len(stripped)
        while indent_stack and indent < indent_stack[-1]:
            indent_stack.pop()
            depth = max(0, depth - 1)
        is_block = stripped.startswith(("for ", "while ", "if ", "elif ", "else:", "try:", "except", "with ", "def ", "class "))
        nesting_per_line.append(depth)
        if is_block and stripped.endswith(":"):
            indent_stack.append(indent + 4)
            depth += 1

    return {
        "total_lines": total_lines,
        "blank_lines": blank_lines,
        "comment_lines": comment_lines,
        "code_lines": total_lines - blank_lines - comment_lines,
        "loops": loops,
        "conditions": conditions,
        "functions": functions,
        "classes": classes,
        "list_comprehensions": list_comps,
        "lambdas": lambdas,
        "imports": imports,
        "max_nesting_depth": max_nesting,
        "function_nesting": function_nesting,
        "nesting_per_line": nesting_per_line,
    }


def ask_ai(code):
    prompt = f"""You are an expert Python code reviewer. Analyze the code below and respond ONLY using the exact XML tags shown. Do not add any text outside the tags. Keep every section brief and focused.

RULES:
- Optimized code must use the EXACT same algorithm — only improve naming, structure, or readability.
- Do NOT swap the algorithm for a different one.
- Keep suggestions and explanations concise (1-2 sentences max per point).

Respond in this exact structure:

[ALGORITHM]
One sentence describing the algorithm used.
[/ALGORITHM]

[COMPLEXITY]
Big-O notation only, e.g. O(n log n) — average case
[/COMPLEXITY]

[SUGGESTIONS]
1. First specific improvement suggestion (one sentence)
2. Second specific improvement suggestion (one sentence)
[/SUGGESTIONS]

[OPTIMIZATION_TYPE]
2-3 sentences explaining what structural/readability changes were made.
[/OPTIMIZATION_TYPE]

[OPTIMIZED_CODE]
(full working optimized Python code only — no comments, no explanation)
[/OPTIMIZED_CODE]

[ALTERNATIVES]
Algorithm Name - O(complexity) - one-line description
Algorithm Name - O(complexity) - one-line description
[/ALTERNATIVES]

[WHY_BETTER]
1-2 sentences on why the optimized version is better.
[/WHY_BETTER]

Code to analyze:
{code}"""

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2500,
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
            return "[AI_SERVICE_ERROR] " + str(result["error"])

        return str(result)

    except Exception as e:
        return "[AI_SERVICE_ERROR] " + str(e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "empty"}), 400

    lines = code.split("\n")
    if len(lines) > MAX_LINES:
        return jsonify({
            "error": "too_long",
            "detail": f"Your code has {len(lines)} lines. Maximum allowed is {MAX_LINES}."
        }), 400

    if len(code) > MAX_CHARS:
        return jsonify({
            "error": "too_long",
            "detail": f"Your code exceeds the {MAX_CHARS} character limit."
        }), 400

    static = analyze_code_ast(code)

    ai_result = ask_ai(code)

    return jsonify({
        "static": static,
        "ai": ai_result,
        "original_code": code
    })


if __name__ == "__main__":
    app.run(debug=True)