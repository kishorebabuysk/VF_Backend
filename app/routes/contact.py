from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse,BulkDeleteRequest
from app.utils.jwt_dependency import get_current_admin

router = APIRouter(
    prefix="/contact",
    tags=["Contact"]
)


# 🔓 PUBLIC – SUBMIT CONTACT FORM
@router.post("/contact", response_model=ContactResponse)
def submit_contact(
    data: ContactCreate,
    db: Session = Depends(get_db)
):
    contact = Contact(**data.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


# 🔐 ADMIN – VIEW CONTACT MESSAGES
@router.get("/admin/contacts", response_model=list[ContactResponse])
def list_contacts(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return (
        db.query(Contact)
        .order_by(Contact.created_at.desc())
        .all()
    )

@router.get("/admin/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.delete("/bulk-delete")
def bulk_delete_contacts(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    contacts = db.query(Contact).filter(
        Contact.id.in_(payload.contact_ids)
    ).all()

    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found")

    for contact in contacts:
        db.delete(contact)

    db.commit()

    return {
        "message": f"{len(contacts)} contacts deleted successfully"
    }

@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()

    return {"message": "Contact deleted successfully"}


