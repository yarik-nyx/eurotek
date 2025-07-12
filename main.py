from docxtpl import DocxTemplate
from docx import Document
from datetime import datetime
from docx.shared import Pt
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import uvicorn
from fpdf import FPDF

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

def fill_contract_jinja(data):
    context = {
        'num_order': '777',
        'date_order': datetime.now().strftime('%d.%m.%Y'),
        'first_name': data['customer']['first_name'],
        'last_name': data['customer']['last_name'],
        'phone_num': data['customer']['phone_num'],
        'all_num': data['customer']['all_num'],
        'all_sum': data['customer']['all_sum'],
        'services': data['items'],
        'total': sum(s['qty'] * s['price'] for s in data['items'])
    }
    doc = DocxTemplate('template.docx')
    doc.render(context)
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    pdf_stream = convert_docx_bytesio_to_pdf_bytesio(output_stream)
    return pdf_stream

def docx_stream_to_code_text(docx_stream: io.BytesIO) -> str:
    docx_stream.seek(0)
    document = Document(docx_stream)
    code_lines = [para.text for para in document.paragraphs]
    return '\n'.join(code_lines)

def code_text_to_pdf(code_text: str) -> io.BytesIO:
    pdf_stream = io.BytesIO()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font('microsoftsansserif', '', 'microsoftsansserif.ttf', uni=True)
    pdf.set_font("microsoftsansserif", size=10)

    for line in code_text.split('\n'):
        pdf.multi_cell(0, 5, line)

    pdf_bytes = pdf.output(dest='S').encode('utf-8')  # 'S' = return as string
    pdf_stream = io.BytesIO(pdf_bytes)
    pdf_stream.seek(0)
    return pdf_stream

# Пример: docx → pdf через BytesIO
def convert_docx_bytesio_to_pdf_bytesio(docx_stream: io.BytesIO) -> io.BytesIO:
    code_text = docx_stream_to_code_text(docx_stream)
    return code_text_to_pdf(code_text)


@app.post("/fill_template")
async def fill_template(
    data = Body(...)
):
    try:
        output_stream = fill_contract_jinja(data)
        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=output.pdf"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port=10000, reload=True)
