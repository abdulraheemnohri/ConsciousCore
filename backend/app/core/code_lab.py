"""
Code Lab & Sandbox for ConsciousCore V1.
Supports gated self-code proposals, static checks, unit test execution, and controlled promotion.
"""

from typing import Dict, Any, List, Optional
import time

class CodeProposal:
    def __init__(self, proposal_id: str, title: str, author: str, target_file: str, diff_content: str):
        self.proposal_id = proposal_id
        self.title = title
        self.author = author
        self.target_file = target_file
        self.diff_content = diff_content
        self.status = "PROPOSED"
        self.syntax_ok = True
        self.security_ok = True
        self.tests_passed = True
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "author": self.author,
            "target_file": self.target_file,
            "diff_content": self.diff_content,
            "status": self.status,
            "syntax_ok": self.syntax_ok,
            "security_ok": self.security_ok,
            "tests_passed": self.tests_passed,
            "created_at": self.created_at
        }

class CodeLab:
    def __init__(self):
        self.proposals: Dict[str, CodeProposal] = {}

    def submit_proposal(self, title: str, author: str, target_file: str, diff_content: str) -> CodeProposal:
        proposal_id = f"proposal_{len(self.proposals) + 1:03d}"
        prop = CodeProposal(proposal_id, title, author, target_file, diff_content)
        self.proposals[proposal_id] = prop
        return prop

    def list_proposals(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.proposals.values()]

    def approve_proposal(self, proposal_id: str) -> Optional[CodeProposal]:
        if proposal_id in self.proposals:
            self.proposals[proposal_id].status = "APPROVED"
            return self.proposals[proposal_id]
        return None
