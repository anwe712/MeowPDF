import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import textwrap
from llama_cpp import Llama

# Load local LLaMA model (change path if needed)
llm = Llama(model_path="./tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")

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
    c.setFont("Helvetica", 12)  # Using default font

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

def main():
    input_pdf = "questions.pdf"
    output_pdf = "QnA_Output_Offline.pdf"

    questions = extract_questions_from_pdf(input_pdf)
    generate_qna_pdf(questions, output_pdf)
    print(f"✅ Done! Output saved as {output_pdf}")

if __name__ == "__main__":
    main()
