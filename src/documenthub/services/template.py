from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SyntheticRecord:
    topic:str
    title:str
    body:str
    question: str
    expected_answer: str

_TEMPLATES: dict[str, tuple[str, str, str, str]] = {
    "leave_policy": (
        "Leave Policy",
        "Employees receive 18 paid leave days per calendar year. "
        "Leave requests must be submitted to the team manager at least "
        "5 working days before the planned leave. Unused paid leave does "
        "not carry forward to the next calendar year.",
        "How many paid leave days does an employee receive each year?",
        "Employees receive 18 paid leave days per calendar year.",
    ),
    "it_support": (
        "IT Support Policy",
        "Employees can contact the IT Help Desk at helpdesk@example.test. "
        "The standard response target for a normal-priority ticket is "
        "within 8 business hours. Critical incidents should be reported "
        "by telephone to the on-call support team.",
        "What is the response target for a normal-priority IT ticket?",
        "The standard response target is within 8 business hours.",
    ),
    "expense_policy": (
        "Expense Policy",
        "The maximum reimbursable meal expense is 30 currency units per "
        "employee per day. Employees must submit itemized receipts within "
        "10 calendar days after the expense. Alcohol is not reimbursable.",
        "What is the daily meal reimbursement limit?",
        "The daily meal reimbursement limit is 30 currency units per employee.",
    ),
}

def get_available_topics()->tuple[str,...]:
    return tuple(sorted(_TEMPLATES))
def create_record(topic:str, index:int, dataset_id:str)->SyntheticRecord:
    try:
        title, body, question, answer = _TEMPLATES[topic]
    except KeyError as exc:
        raise ValueError(f"unknown topic '{topic}'. Available topics: {get_available_topics()} ") from exc
    document_id = f"{dataset_id}-{index:05d}"
    document_text = (
        f"{title}\n"
        f"Document ID: {document_id}\n"
        f"Topic: {topic}\n"
        f"Author: DOCUMENTHUB\n\n"
        f"Body: {body}\n"
    )

    return SyntheticRecord(
        topic= topic,
        title=title,
        body= document_text,
        question=question,
        expected_answer=answer
    )
