import os
from flask import Flask, render_template, request, send_file
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import textwrap
from llama_cpp import Llama

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

llm = Llama(model_path="./tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", n_threads=4)

def extract_questions_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    questions = text.strip().split('\n')
    return [q.strip() for q in questions if q.strip()]

def get_answer_local_llm(question):
    prompt = f"You are a helpful assistant. Answer the following question:\n{question}\nAnswer:"
    output = llm(prompt, max_tokens=200, stop=["\n"])
    return output['choices'][0]['text'].strip()

def generate_qna_pdf(questions, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)

    x_margin = 50
    y_position = height - 60
    line_height = 18

    for idx, question in enumerate(questions, 1):
        answer = get_answer_local_llm(question)

        q_text = f"Q{idx}: {question}"
        a_text = f"Ans: {answer}"

        for line in textwrap.wrap(q_text, width=95):
            c.drawString(x_margin, y_position, line)
            y_position -= line_height
        
        y_position -= 5

        for line in textwrap.wrap(a_text, width=95):
            c.drawString(x_margin, y_position, line)
            y_position -= line_height

        y_position -= 20

        if y_position < 100:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 60

    c.save()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["pdf"]
        if uploaded_file.filename.endswith(".pdf"):
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)

            questions = extract_questions_from_pdf(file_path)
            output_pdf_path = os.path.join(OUTPUT_FOLDER, "Meow_QnA_Output.pdf")
            generate_qna_pdf(questions, output_pdf_path)

            return send_file(output_pdf_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
