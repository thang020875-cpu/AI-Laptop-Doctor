"""
AI Laptop Doctor
Symptom Session Manager v3

Giữ lại toàn bộ session v2 và bổ sung:
- step_history
- current_step
- verification_results
- cập nhật evidence sau bước kiểm tra
"""

from datetime import datetime

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.symptom_question_engine import (
    build_evidence,
    get_question,
    get_next_question,
)


SESSIONS = {}


def create_session(session_id, symptom):
    session = {
        "session_id": session_id,
        "symptom": symptom,
        "answers": [],
        "evidence": [],
        "question_index": 0,

        # Diagnostic Brain v2
        "step_history": [],
        "current_step": None,
        "verification_results": [],

        "status": "ACTIVE",
        "diagnosis": None,
        "last_action": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    SESSIONS[session_id] = session
    return session


def get_session(session_id):
    return SESSIONS.get(session_id)


def update_session(session):
    session["updated_at"] = datetime.now().isoformat()
    return session


def save_answer(session_id, question_id, question, answer):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    existing_answer = None

    for item in session["answers"]:
        if item["question_id"] == question_id:
            existing_answer = item
            break

    if existing_answer:
        existing_answer["answer"] = answer
    else:
        session["answers"].append({
            "question_id": question_id,
            "question": question,
            "answer": answer,
        })

    session["evidence"] = build_evidence(
        session["symptom"]["code"],
        session["answers"],
    )

    answered_ids = [
        item["question_id"]
        for item in session["answers"]
    ]

    next_question = get_next_question(
        session["symptom"]["code"],
        answered_ids,
    )

    if next_question:
        questions = []
        index = 0

        while True:
            question = get_question(
                session["symptom"]["code"],
                index,
            )

            if question is None:
                break

            questions.append(question)
            index += 1

        for i, item in enumerate(questions):
            if item["id"] == next_question["id"]:
                session["question_index"] = i
                break

        session["status"] = "ACTIVE"
        session["last_action"] = "ANSWER_SAVED"

    else:
        session["question_index"] = len(session["answers"])
        session["status"] = "READY_FOR_DIAGNOSIS"
        session["last_action"] = "QUESTIONNAIRE_COMPLETE"

    update_session(session)
    return session


def get_current_question(session_id):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    if session["status"] != "ACTIVE":
        return None

    return get_question(
        session["symptom"]["code"],
        session["question_index"],
    )


def get_evidence(session_id):
    session = SESSIONS.get(session_id)

    if not session:
        return []

    return session.get("evidence", [])


def add_verification_result(
    session_id,
    answer,
    evidence,
):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    for item in evidence:
        if item not in session["evidence"]:
            session["evidence"].append(item)

    session.setdefault(
        "verification_results",
        []
    ).append({
        "answer": answer,
        "evidence": evidence,
        "step_id": (
            session.get("current_step", {})
            .get("id")
        ),
    })

    update_session(session)
    return session


def set_current_step(session_id, step):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    session["current_step"] = step

    if step:
        session.setdefault(
            "step_history",
            []
        ).append({
            "step_id": step.get("id"),
            "title": step.get("title"),
        })

        session["status"] = "WAITING_FOR_VERIFICATION"
        session["last_action"] = "BRAIN_NEXT_STEP"

    else:
        session["status"] = "DIAGNOSED"
        session["last_action"] = "BRAIN_DIAGNOSIS_COMPLETE"

    update_session(session)
    return session


def set_diagnosis(session_id, diagnosis):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    session["diagnosis"] = diagnosis

    next_step = diagnosis.get("next_step")
    session["current_step"] = next_step

    if next_step:
        history = session.setdefault("step_history", [])
        step_id = next_step.get("id")

        if not history or history[-1].get("step_id") != step_id:
            history.append({
                "step_id": step_id,
                "title": next_step.get("title", "")
            })

        session["status"] = "WAITING_FOR_VERIFICATION"
        session["last_action"] = "BRAIN_NEXT_STEP"
    else:
        session["status"] = "DIAGNOSED"
        session["last_action"] = "BRAIN_DIAGNOSIS_COMPLETE"

    update_session(session)
    return session


def mark_waiting_verification(session_id):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    session["status"] = "WAITING_FOR_VERIFICATION"
    session["last_action"] = "WAITING_FOR_USER_TEST"

    update_session(session)
    return session


def continue_session(session_id):
    session = SESSIONS.get(session_id)

    if not session:
        return None

    session["status"] = "ACTIVE"
    session["last_action"] = "SESSION_CONTINUED"

    update_session(session)
    return session


def finish_session(session_id):
    session = SESSIONS.get(session_id)

    if session:
        session["status"] = "COMPLETED"
        session["last_action"] = "SESSION_COMPLETED"

        update_session(session)

    return session


def clear_session(session_id):
    SESSIONS.pop(
        session_id,
        None
    )
