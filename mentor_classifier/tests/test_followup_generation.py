#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from mentor_classifier.types import Answer, AnswerInfo

import pytest
import responses

from .helpers import (
    fixture_mentor_data,
    load_mentor_csv,
)
from mentor_classifier.ner import NamedEntities
from .helpers import get_answers
from typing import List, Dict


@responses.activate
@pytest.mark.parametrize(
    "mentor_id, expected_answer",
    [("clint", {"people": ["Clint Anderson"], "places": [], "acronyms": []})],
)
def test_recognizes_named_entities(
    mentor_id: str,
    expected_answer: Dict[str, List[str]],
    shared_root: str,
):
    mentor = load_mentor_csv(fixture_mentor_data(mentor_id, "data.csv"))
    answers: List[Answer] = get_answers(mentor)
    answer_info: List[AnswerInfo] = [
        AnswerInfo(
            question_text=answer.question.question, answer_text=answer.transcript
        )
        for answer in answers
    ]
    ents = NamedEntities(answer_info, shared_root)
    assert NamedEntities.to_dict(ents) == expected_answer


@responses.activate
@pytest.mark.parametrize(
    "mentor_id, expected_question",
    [("clint", "Can you tell me more about Clint Anderson?")],
)
def test_generates_followups(
    mentor_id: str,
    expected_question: str,
    shared_root: str,
):
    mentor = load_mentor_csv(fixture_mentor_data(mentor_id, "data.csv"))
    answers: List[Answer] = get_answers(mentor)
    answer_info: List[AnswerInfo] = [
        AnswerInfo(
            question_text=answer.question.question, answer_text=answer.transcript
        )
        for answer in answers
    ]
    ents = NamedEntities(answer_info, shared_root)
    questions = ents.generate_questions()
    actual_question = questions[0].question
    assert actual_question == expected_question
