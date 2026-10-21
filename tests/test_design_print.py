"""Exercise real pagination so decorative changes cannot hide CV content."""
import pytest

from app.schemas import CvDocument, ResumeDesign
from app.services.design import designed_html
from app.services.pdf import _configure_pdf_libraries
from tests.samples import SAMPLE_PROFILE


@pytest.mark.parametrize('template', ['classic', 'modern', 'creative', 'minimal'])
def test_long_cv_keeps_every_bullet_inside_printable_pages(template):
    _configure_pdf_libraries()
    from weasyprint import HTML

    document = CvDocument.model_validate(SAMPLE_PROFILE.model_dump())
    role = document.experience[0]
    document.experience = [role.model_copy(update={
        'employer': f'Employer {index}',
        'bullets': [f'Record {index}-{bullet}: Built reliable applications and documented the work for the delivery team.'
                    for bullet in range(4)],
    }) for index in range(8)]
    rendered = HTML(string=designed_html(document, ResumeDesign(template=template))).render()
    assert len(rendered.pages) > 1
    words = []
    for page in rendered.pages:
        boxes = [box for box in page._page_box.descendants() if type(box).__name__ == 'TextBox']
        assert boxes, 'Decoration must not create blank pages'
        for index, box in enumerate(boxes):
            for other in boxes[index + 1:]:
                overlap_x = min(box.position_x + box.width, other.position_x + other.width) - max(box.position_x, other.position_x)
                overlap_y = min(box.position_y + box.height, other.position_y + other.height) - max(box.position_y, other.position_y)
                assert overlap_x <= 1 or overlap_y <= 1, (box.text, other.text)
            assert 59 <= box.position_x and box.position_x + box.width <= page.width - 59
            assert 59 <= box.position_y and box.position_y + box.height <= page.height - 59
            words.append(box.text)
    text = ' '.join(words)
    for index in range(8):
        for bullet in range(4):
            assert text.count(f'Record {index}-{bullet}:') == 1
