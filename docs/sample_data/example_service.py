class TicketRouter:
    def create_ticket(self, title: str, severity: str) -> dict:
        return {"title": title, "severity": severity, "status": "open"}


def build_trace_id(prefix: str, value: str) -> str:
    return f"{prefix}-{value}"
