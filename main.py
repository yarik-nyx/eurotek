from docxtpl import DocxTemplate
from datetime import datetime
from docx.shared import Pt
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import io
import uvicorn
from typing import Dict, Any

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
    return output_stream


@app.post("/fill_template")
async def fill_template(
    data = Body(...)
):
    try:
        output_stream = fill_contract_jinja(data)
        return StreamingResponse(
            output_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=output.docx"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port=10000, reload=True)
