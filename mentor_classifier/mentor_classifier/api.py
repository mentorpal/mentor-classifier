#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import json
import os
import requests

from mentor_classifier.mentor import MentorConfig, mentor_config_from_dict

GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT") or "http://graphql/graphql"


def fetch_mentor_data(mentor: str) -> MentorConfig:
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json={
            "query": f"""query {{
                mentor(id: "{mentor}") {{
                    name
                    firstName
                    title
                    subjects {{
                        _id
                        name
                        questions {{
                            _id
                            topics {{
                                _id
                                name
                            }}
                        }}
                    }}
                    answers {{
                        _id
                        question {{
                            _id
                            question
                            paraphrases
                            type
                            name
                            topics {{
                                _id
                                name
                            }}
                        }}
                        status
                        transcript
                        video
                    }}
                }}
            }}"""
        },
    )
    res.raise_for_status()
    tdjson = res.json()
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    return mentor_config_from_dict(tdjson["data"]["mentor"])


def update_training(mentor: str):
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json={
            "query": f"""mutation {{
                updateMentorTraining(id: "{mentor}") {{
                    _id
                }}
            }}"""
        },
    )
    res.raise_for_status()


def create_user_question(mentor: str, question: str, answer_id: str, confidence: float):
    res = requests.post(
        GRAPHQL_ENDPOINT,
        json={
            "query": f"""mutation {{
                userQuestionCreate(userQuestion: {{
                    question: "{question}",
                    mentor: "{mentor}",
                    classifierAnswer: "{answer_id}",
                    confidence: {confidence}
                }}) {{
                    _id
                }}
            }}"""
        },
    )
    res.raise_for_status()
    tdjson = res.json()
    if "errors" in tdjson:
        raise Exception(json.dumps(tdjson.get("errors")))
    # TODO: should throw an error but need to figure out how to mock 2 different GQL queries...
    try:
        return tdjson["data"]["userQuestionCreate"]["_id"]
    except KeyError:
        return "error"