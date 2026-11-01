"""Source catalog and cache identity for Ollama-generated application insights."""
import hashlib
import json

INSIGHTS_VERSION = 3


def fingerprint(role, board, document, job_description=''):
    return hashlib.sha256(json.dumps([INSIGHTS_VERSION, role, board, document, job_description], sort_keys=True).encode()).hexdigest()


def evidence_catalog(document):
    evidence = {}
    for index, skill in enumerate(document.get('skills', [])):
        evidence[f's{index}'] = {'kind': 'skill', 'text': skill}
    for index, work in enumerate(document.get('experience', [])):
        identity = {key: work.get(key, '') for key in ('employer', 'title', 'start', 'end')}
        evidence[f'w{index}'] = {'kind': 'role', 'text': json.dumps(identity), **identity}
        for number, bullet in enumerate(work.get('bullets', [])):
            evidence[f'w{index}b{number}'] = {'kind': 'work', 'text': bullet, **identity}
    for index, school in enumerate(document.get('education', [])):
        evidence[f'e{index}'] = {'kind': 'education', 'text': json.dumps(school)}
    if document.get('summary'):
        evidence['summary'] = {'kind': 'summary', 'text': document['summary']}
    for index, section in enumerate(document.get('custom_sections', [])):
        for number, item in enumerate(section.get('items', [])):
            evidence[f'c{index}i{number}'] = {'kind': 'additional', 'text': item, 'section': section.get('title', '')}
    return evidence
