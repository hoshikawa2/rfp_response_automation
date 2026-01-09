from flask import Flask, render_template, request, jsonify
import traceback
import json

# 🔥 IMPORTA SEU PIPELINE
from oci_genai_llm_graphrag_financial import answer_question

app = Flask(__name__)

def parse_llm_json(raw: str) -> dict:
    try:
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        return json.loads(raw)
    except Exception:
        return {
            "answer": "ERROR",
            "justification": "LLM returned invalid JSON",
            "raw_output": raw
        }

# =========================
# Health check (Load Balancer)
# =========================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "UP"}), 200


# =========================
# Página Web
# =========================
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# =========================
# Endpoint de Chat
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Empty question"}), 400

        raw_answer = answer_question(question)
        parsed_answer = parse_llm_json(raw_answer)

        return jsonify({
            "question": question,
            "result": parsed_answer
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8100,
        debug=False
    )