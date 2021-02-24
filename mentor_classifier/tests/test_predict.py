#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path

import json
import pytest
import responses

from mentor_classifier.classifier.train import ClassifierTraining
from mentor_classifier.classifier.predict import Classifier
from .helpers import fixture_mentor, fixture_path


@pytest.fixture(scope="module")
def data_root() -> str:
    return fixture_path("data")


@pytest.fixture(scope="module")
def shared_root(word2vec) -> str:
    return path.dirname(word2vec)


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,question,expected_answer_id,expected_answer",
    [
        ("clint", "What is your name?", "A1", "Clint Anderson"),
        ("clint", "How old are you?", "A2", "37 years old"),
        ("clint", "Who are you?", "A1", "Clint Anderson"),
        ("clint", "What's your age?", "A2", "37 years old"),
    ],
)
def test_gets_answer_for_exact_match_and_paraphrases(
    tmpdir,
    data_root: str,
    shared_root: str,
    mentor_id: str,
    question: str,
    expected_answer_id: str,
    expected_answer: str,
):
    mentor = fixture_mentor(mentor_id)
    with open(fixture_path("graphql/feedback.json")) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    if not path.exists(path.join(data_root, mentor_id)):
        training = ClassifierTraining(mentor, shared_root, data_root)
        training.train()
        training.save()
    classifier = Classifier(mentor, shared_root, data_root)
    answer_id, answer, confidence, feedback_id = classifier.evaluate(question)
    assert answer_id == expected_answer_id
    assert answer == expected_answer
    assert confidence == 1
    assert feedback_id is None


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,question,expected_answer_id,expected_answer",
    [
        ("clint", "What's your name?", "A1", "Clint Anderson"),
        ("clint", "Tell me your name", "A1", "Clint Anderson"),
    ],
)
def test_predicts_answer(
    tmpdir,
    data_root: str,
    shared_root: str,
    mentor_id: str,
    question: str,
    expected_answer_id: str,
    expected_answer: str,
):
    mentor = fixture_mentor(mentor_id)
    with open(fixture_path("graphql/feedback.json")) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    if not path.exists(path.join(data_root, mentor_id)):
        training = ClassifierTraining(mentor, shared_root, data_root)
        training.train()
        training.save()
    classifier = Classifier(mentor, shared_root, data_root)
    answer_id, answer, confidence, feedback_id = classifier.evaluate(question)
    assert answer_id == expected_answer_id
    assert answer == expected_answer
    assert confidence != 1
    assert feedback_id is not None


@responses.activate
@pytest.mark.parametrize(
    "mentor_id,question,expected_answer_id,expected_answer",
    [
        ("clint", "What is your age?", "A6", "Ask me something else"),
    ],
)
def test_gets_off_topic(
    tmpdir,
    data_root: str,
    shared_root: str,
    mentor_id: str,
    question: str,
    expected_answer_id: str,
    expected_answer: str,
):
    mentor = fixture_mentor(mentor_id)
    with open(fixture_path("graphql/feedback.json")) as f:
        data = json.load(f)
    responses.add(responses.POST, "http://graphql/graphql", json=data, status=200)
    if not path.exists(path.join(data_root, mentor_id)):
        training = ClassifierTraining(mentor, shared_root, data_root)
        training.train()
        training.save()
    classifier = Classifier(mentor, shared_root, data_root)
    answer_id, answer, confidence, feedback_id = classifier.evaluate(question)
    assert answer_id == expected_answer_id
    assert answer == expected_answer
    assert confidence < 0
    assert feedback_id is not None