"""
Manual script to update feedback in the database.
Use this if the automatic reroll detection isn't working.
"""
import sys
import os
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server')))

from app.database.session import SessionLocal
from app.models import prompt as models
from sqlalchemy import desc

def list_recent_sessions(db, limit=20):
    """List recent sessions that haven't been rejected."""
    entries = db.query(models.UsageAnalytics).filter(
        models.UsageAnalytics.user_action != models.UserAction.rejected
    ).order_by(desc(models.UsageAnalytics.created_at)).limit(limit).all()
    
    print("\n" + "=" * 80)
    print(f"Recent sessions (showing up to {limit}):")
    print("=" * 80)
    for entry in entries:
        action_status = entry.user_action.value if entry.user_action else "None (defaults to accepted)"
        print(f"ID: {entry.id} | Session: {entry.session_id} | Action: {action_status} | Created: {entry.created_at}")
    print("=" * 80 + "\n")
    return entries

def mark_as_rejected(session_id_str: str):
    """Manually mark a session as rejected."""
    try:
        session_id = uuid.UUID(session_id_str)
    except ValueError:
        print(f"❌ Invalid session ID format: {session_id_str}")
        return False
    
    db = SessionLocal()
    try:
        entry = db.query(models.UsageAnalytics).filter(
            models.UsageAnalytics.session_id == session_id
        ).order_by(desc(models.UsageAnalytics.created_at)).first()
        
        if not entry:
            print(f"❌ No entry found for session_id: {session_id}")
            return False
        
        old_action = entry.user_action.value if entry.user_action else "None"
        entry.user_action = models.UserAction.rejected
        db.commit()
        
        print(f"✅ Updated session {session_id}")
        print(f"   Old action: {old_action}")
        print(f"   New action: rejected")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating: {e}")
        return False
    finally:
        db.close()

def mark_last_n_as_rejected(n: int):
    """Mark the last N accepted entries as rejected."""
    db = SessionLocal()
    try:
        entries = db.query(models.UsageAnalytics).filter(
            models.UsageAnalytics.user_action != models.UserAction.rejected
        ).order_by(desc(models.UsageAnalytics.created_at)).limit(n).all()
        
        if not entries:
            print("❌ No entries found to reject")
            return 0
        
        count = 0
        for entry in entries:
            entry.user_action = models.UserAction.rejected
            count += 1
        
        db.commit()
        print(f"✅ Marked {count} entries as rejected")
        return count
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    db = SessionLocal()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_recent_sessions(db)
        
        elif command == "reject" and len(sys.argv) > 2:
            if sys.argv[2].isdigit():
                # Mark last N as rejected
                n = int(sys.argv[2])
                db.close()
                mark_last_n_as_rejected(n)
            else:
                # Mark specific session_id as rejected
                session_id = sys.argv[2]
                db.close()
                mark_as_rejected(session_id)
        
        elif command == "stats":
            total = db.query(models.UsageAnalytics).count()
            accepted = db.query(models.UsageAnalytics).filter(
                models.UsageAnalytics.user_action == models.UserAction.accepted
            ).count()
            rejected = db.query(models.UsageAnalytics).filter(
                models.UsageAnalytics.user_action == models.UserAction.rejected
            ).count()
            none_action = db.query(models.UsageAnalytics).filter(
                models.UsageAnalytics.user_action.is_(None)
            ).count()
            
            print("\n" + "=" * 80)
            print("Database Statistics:")
            print("=" * 80)
            print(f"Total entries: {total}")
            print(f"Accepted: {accepted}")
            print(f"Rejected: {rejected}")
            print(f"No action (default accepted): {none_action}")
            print("=" * 80 + "\n")
        
        else:
            print("Usage:")
            print("  python scripts/manual_feedback.py list          - List recent sessions")
            print("  python scripts/manual_feedback.py stats         - Show statistics")
            print("  python scripts/manual_feedback.py reject N      - Mark last N as rejected")
            print("  python scripts/manual_feedback.py reject <uuid>  - Mark specific session as rejected")
    else:
        # Default: show stats
        total = db.query(models.UsageAnalytics).count()
        accepted = db.query(models.UsageAnalytics).filter(
            models.UsageAnalytics.user_action == models.UserAction.accepted
        ).count()
        rejected = db.query(models.UsageAnalytics).filter(
            models.UsageAnalytics.user_action == models.UserAction.rejected
        ).count()
        none_action = db.query(models.UsageAnalytics).filter(
            models.UsageAnalytics.user_action.is_(None)
        ).count()
        
        print("\n" + "=" * 80)
        print("Database Statistics:")
        print("=" * 80)
        print(f"Total entries: {total}")
        print(f"Accepted: {accepted}")
        print(f"Rejected: {rejected}")
        print(f"No action (default accepted): {none_action}")
        print("=" * 80)
        print("\nUsage:")
        print("  python scripts/manual_feedback.py list          - List recent sessions")
        print("  python scripts/manual_feedback.py reject N      - Mark last N as rejected")
        print("  python scripts/manual_feedback.py reject <uuid>  - Mark specific session as rejected")
        print()
    
    db.close()

