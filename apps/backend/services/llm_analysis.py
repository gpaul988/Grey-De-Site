import openai
from django.conf import settings
import PyPDF2
import docx

openai.api_key = settings.OPENAI_API_KEY


def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file"""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text


def extract_text_from_docx(file_path):
    """Extracts text from a Word document"""
    doc = docx.Document(file_path)
    return " ".join([p.text for p in doc.paragraphs])


def analyze_file_content(file_path):
    """Uses LLM to analyze file content and suggest services"""
    file_extension = file_path.split(".")[-1].lower()

    if file_extension == "pdf":
        content = extract_text_from_pdf(file_path)
    elif file_extension == "docx":
        content = extract_text_from_docx(file_path)
    else:
        return "Unsupported file type"

    prompt = f"""
    Analyze the following client request and suggest the best Grey Infotech services.
    Provide an estimated completion time based on complexity.

    Client Request:
    {content}

    Response format:
    - Recommended Services:
    - Estimated Time to Complete:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert IT service consultant."},
                  {"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]
