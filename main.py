import os

from models.creditors_model import Creditor
from models.inquiries_model import Inquirie

from fastapi import FastAPI, Response, UploadFile, File
from starlette.responses import StreamingResponse
from io import BytesIO
import fitz




def extract_text_from_pdf(doc):
    all_text = ""

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text()
        all_text += text + "\n\n"  # Adiciona o texto da página com uma quebra de linha entre as páginas

    doc.close()
    return all_text


app = FastAPI()


# route to return the pdf file Reports(1).pdf in same directory
@app.get("/pdf_by_id/{pdf_id}")
async def get_pdf(pdf_id: str):
    """
    Retorna um pdf para poder vizualizar \n
    Copie a URL do campo "Request URL" para visualizar o PDF no seu navegador \n
    :param item_id: ID id do pdf Range (1- 3)

    """
    file_path = f'./reports/Reports({pdf_id}).pdf'
    print(file_path)
    if os.path.exists(file_path):
        file_stream = open(file_path, 'rb')
        return StreamingResponse(file_stream, media_type='application/pdf')

    return Response(content="File not found", status_code=404)


@app.post("/extract_object")
async def extract_object_from_pdf(pdf_file: UploadFile = File(...)):
    """
    Retorna um Json com as informações coletadas do PDF \n
    Copie a URL do campo "Request URL" para visualizar o PDF no seu navegador \n

    """
    if pdf_file.filename.endswith('.pdf'):
        try:
            contents = await pdf_file.read()
            doc = fitz.open(stream=BytesIO(contents))

            text = extract_text_from_pdf(doc)

            name = ''
            address = ''
            score = ''
            ssn = ''

            lines = text.split('\n')

            for idx, line in enumerate(lines):
                if 'Other Name' in line:
                    name = lines[idx + 1]

                if 'Other Address(es)' in line:
                    address = lines[idx + 1]
                    address += lines[idx + 2]

                if '(Score range: 300-850)' in line:
                    score = lines[idx + 1]

                if 'Date of Birth' in line:
                    ssn = lines[idx + 1]

            inquiries = Inquirie.extract_inquiries(text)
            creditors = Creditor.extract_creditors(text)

            extracted_object = {
                "score": score,
                "address": address,
                "name": name,
                "ssn": ssn,
                "creditors": creditors,
                "inquiries": inquiries
            }

            return extracted_object

        except Exception as e:
            return {"error": f"Error processing PDF: {str(e)}"}
    else:
        return {"error": "Please provide a PDF file."}


