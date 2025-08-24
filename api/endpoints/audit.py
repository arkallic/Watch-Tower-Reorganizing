from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

# This router will handle all requests starting with /audit
router = APIRouter(prefix="/audit", tags=["audit"])

# Global dependency - this will be injected when the API starts
audit_logger = None

def initialize_dependencies(audit_logger_instance):
    """Allows the main API app to pass in the audit_logger instance."""
    global audit_logger
    audit_logger = audit_logger_instance

@router.get("/logs")
async def get_audit_logs(
    page: int = 1,
    limit: int = 25, # Default limit matches the frontend
    event_type: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None)
):
    """
    Get paginated and filterable audit logs for the Timeline feature.
    """
    if not audit_logger:
        raise HTTPException(status_code=503, detail="Audit Logger is not available.")

    try:
        all_logs = audit_logger.get_logs()

        # --- Filtering Logic (optional for now, but good to have) ---
        if event_type:
            all_logs = [log for log in all_logs if log.get("event_type") == event_type]
        if actor_id:
            all_logs = [log for log in all_logs if str(log.get("actor", {}).get("id")) == actor_id]

        # --- Pagination Logic ---
        total_items = len(all_logs)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_logs = all_logs[start_index:end_index]
        total_pages = (total_items + limit - 1) // limit

        return {
            "total_items": total_items,
            "logs": paginated_logs,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_audit_logs endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while fetching audit logs.")