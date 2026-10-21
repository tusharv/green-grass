"""Small, self-contained vector ornaments shared by screen and print."""
from urllib.parse import quote


def corner_images(template: str, accent: str = '#245747') -> tuple[str, str]:
    ink = accent if len(accent) == 7 and accent.startswith('#') and all(c in '0123456789abcdefABCDEF' for c in accent[1:]) else '#245747'
    opacity = '0.18' if template == 'modern' else '0.38'
    if template == 'modern':
        shapes = ''.join(
            f'<path d="M-30 {-110+i*18}C50 {50+i*18} 200 {-100+i*18} 270 {i*18}S200 {170+i*18} 380 {210+i*18}"/>'
            for i in range(11)
        )
    elif template == 'classic':
        shapes = ''.join(
            f'<path d="M{95+i*10} 0V{75+i*10}Q{95+i*10} {110+i*10} {130+i*10} {110+i*10}H340"/>'
            for i in range(5)
        )
    elif template == 'creative':
        shapes = ''.join(f'<circle cx="350" cy="10" r="{90+i*21}"/>' for i in range(9))
    else:
        shapes = '<path d="M205 0V70H340M225 0V50H340M245 0V30H340"/><path d="M285 100H320M302.5 82.5V117.5"/>'

    def image(transform=''):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="340" height="400" viewBox="0 0 340 400">'
               f'<g transform="{transform}" fill="none" stroke="{ink}" stroke-opacity="{opacity}" stroke-width="1.05">{shapes}</g></svg>')
        return 'url("data:image/svg+xml,' + quote(svg, safe='') + '")'

    return image(), image('translate(340 400) rotate(180)')
