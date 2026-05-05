from sqlalchemy.orm import Session

from app.llm.base import LLMProvider
from app.tools.base import Tool


class GeneratePRSummaryTool(Tool):
    name = "generate_pr_summary"
    description = "Generate a pull request summary, risk areas, and test suggestions from changed files and diff text."
    input_schema = {"changed_files": "string[]", "diff_text": "string", "related_ticket_id": "integer?"}
    output_schema = {"summary": "string", "risk_areas": "string[]", "test_suggestions": "string[]"}

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def execute(self, db: Session, arguments: dict) -> dict:
        changed_files = arguments.get("changed_files", [])
        diff_text = arguments.get("diff_text", "")
        response = self.llm.generate(
            f"Create PR summary for files {changed_files}. Include risk areas and tests.",
            context=f"Diff:\n{diff_text[:5000]}\n[doc:pr-summary-chunk:0]",
        )
        return {"summary": response.text, "risk_areas": ["integration boundaries", "data model changes"], "test_suggestions": ["run unit tests", "exercise affected API endpoints"]}
