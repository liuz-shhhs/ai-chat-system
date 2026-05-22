from fastapi import APIRouter, HTTPException

from model.document_model import DocumentUploadRequest
from service.document_parser import DocumentParseError
from service.rag_service import delete_user_document, get_user_documents, ingest_document

router = APIRouter()


@router.get("/documents")
def get_documents():
    user_id = 1

    try:
        data = get_user_documents(user_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文档列表加载失败: {exc}") from exc

    return {
        "data": data
    }


@router.post("/documents/upload")
def upload_document(req: DocumentUploadRequest):
    user_id = 1

    try:
        data = ingest_document(
            user_id=user_id,
            filename=req.filename,
            content_base64=req.content_base64,
            content_type=req.content_type,
        )
    except DocumentParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文档上传失败: {exc}") from exc

    return data


@router.delete("/documents/{document_id}")
def delete_document(document_id: int):
    user_id = 1

    try:
        deleted = delete_user_document(user_id, document_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文档删除失败: {exc}") from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="文档不存在或无权删除。")

    return {
        "deleted": True,
        "id": document_id,
    }
