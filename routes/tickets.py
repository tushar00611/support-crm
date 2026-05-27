from fastapi import APIRouter, HTTPException
from database import get_db
from models import CreateTicket, UpdateTicket

router = APIRouter()

def generate_ticket_id():
    conn = get_db()
    count = conn.execute(
        "SELECT COUNT(*) FROM tickets"
    ).fetchone()[0]
    conn.close()
    return f"TKT-{str(count + 1).zfill(3)}"

@router.post("/")
def create_ticket(data: CreateTicket):
    ticket_id = generate_ticket_id()
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO tickets
            (ticket_id, customer_name, customer_email,
             subject, description)
            VALUES (?, ?, ?, ?, ?)
        """, (ticket_id, data.customer_name,
              data.customer_email,
              data.subject, data.description))
        conn.commit()
        ticket = conn.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (ticket_id,)
        ).fetchone()
        return {
            "ticket_id": ticket["ticket_id"],
            "created_at": ticket["created_at"]
        }
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        conn.close()

@router.get("/")
def list_tickets(status: str = None, search: str = None):
    conn = get_db()
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += """ AND (
            customer_name  LIKE ? OR
            customer_email LIKE ? OR
            ticket_id      LIKE ? OR
            subject        LIKE ? OR
            description    LIKE ?
        )"""
        s = f"%{search}%"
        params.extend([s, s, s, s, s])
    query += " ORDER BY created_at DESC"
    tickets = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(t) for t in tickets]

@router.get("/{ticket_id}")
def get_ticket(ticket_id: str):
    conn = get_db()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?",
        (ticket_id,)
    ).fetchone()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    notes = conn.execute(
        "SELECT * FROM notes WHERE ticket_id = ? ORDER BY created_at ASC",
        (ticket_id,)
    ).fetchall()
    conn.close()
    result = dict(ticket)
    result["notes"] = [dict(n) for n in notes]
    return result

@router.put("/{ticket_id}")
def update_ticket(ticket_id: str, data: UpdateTicket):
    conn = get_db()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?",
        (ticket_id,)
    ).fetchone()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    allowed = ["Open", "In Progress", "Closed"]
    if data.status and data.status not in allowed:
        raise HTTPException(400,
            f"Status must be one of: {allowed}")
    if data.status:
        conn.execute("""
            UPDATE tickets
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE ticket_id = ?
        """, (data.status, ticket_id))
    if data.note:
        conn.execute(
            "INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)",
            (ticket_id, data.note)
        )
    conn.commit()
    updated = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?",
        (ticket_id,)
    ).fetchone()
    conn.close()
    return {"success": True, "updated_at": updated["updated_at"]}

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: str):
    conn = get_db()
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?",
        (ticket_id,)
    ).fetchone()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    conn.execute(
        "DELETE FROM notes WHERE ticket_id = ?",
        (ticket_id,)
    )
    conn.execute(
        "DELETE FROM tickets WHERE ticket_id = ?",
        (ticket_id,)
    )
    conn.commit()
    conn.close()
    return {"success": True, "deleted": ticket_id}
