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
    decoration_sizes = None
    for page in rendered.pages:
        if template != 'minimal':
            layers = [layer for layer in page._page_box.background.layers if layer.image]
            assert len(layers) >= 2, 'Artwork must have independently positioned pieces'
            sizes = [layer.size for layer in layers]
            if decoration_sizes is not None:
                assert sizes == decoration_sizes, 'Decorations must repeat at the same size on every page'
            decoration_sizes = sizes
            for layer in layers:
                _, _, ratio = layer.image.get_intrinsic_size(1, 16)
                if ratio:
                    assert layer.size[0] / layer.size[1] == pytest.approx(ratio)
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


@pytest.mark.parametrize('template', ['classic', 'modern', 'creative', 'minimal'])
def test_long_job_title_has_full_width_and_dates_below_it(template):
    _configure_pdf_libraries()
    from weasyprint import HTML

    document = CvDocument.model_validate(SAMPLE_PROFILE.model_dump())
    document.experience[0].title = 'Associate Software Development Engineer'
    document.experience[0].start = 'December 2021'
    document.experience[0].end = 'May 2024'
    rendered = HTML(string=designed_html(document, ResumeDesign(template=template))).render()
    boxes = list(rendered.pages[0]._page_box.descendants())
    title = next(box for box in boxes if box.element_tag == 'h3' and type(box).__name__ == 'BlockBox')
    dates = next(box for box in boxes if box.element is not None
                 and box.element.get('class') == 'dates' and type(box).__name__ == 'BlockBox')
    assert title.width > 300, 'Dates must not consume the title column'
    assert dates.position_y >= title.position_y + title.height
    lines = [box.text for box in title.descendants() if type(box).__name__ == 'TextBox']
    assert ' '.join(lines) == document.experience[0].title
