from docxtpl import DocxTemplate
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import uvicorn
import subprocess
import os

def convert_docx_to_pdf(docx_path, output_dir):
    subprocess.run([
        "libreoffice",  # или "libreoffice" в Linux
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        docx_path
    ], check=True)

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
    doc.save('output.docx')


@app.post("/fill_template")
async def fill_template(
    data = Body(...)
):
    try:
        fill_contract_jinja(data)
        convert_docx_to_pdf('output.docx', ".")
        file_path = "output.pdf"  # путь к вашему PDF
        file_like = open(file_path, mode="rb")
        return StreamingResponse(
            file_like,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=contract.pdf"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port=10000, reload=True)
