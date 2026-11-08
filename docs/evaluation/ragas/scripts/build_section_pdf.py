"""Render the manuscript part of thesis-section-draft.md (after the first '---') to a text-based PDF.
Supports ##/### headings, paragraphs, '- ' bullets, '> ' quotes, indented formula lines, pipe tables,
**bold**, *italic* and `code`. Usage: python build_section_pdf.py <draft.md> <out.pdf> [title]
Needs reportlab (present in the research venv)."""
import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONTS = 'C:/Windows/Fonts/'
for name, file in (('Serif', 'times.ttf'), ('Serif-B', 'timesbd.ttf'), ('Serif-I', 'timesi.ttf'),
                   ('Serif-BI', 'timesbi.ttf'), ('Mono', 'cour.ttf')):
    pdfmetrics.registerFont(TTFont(name, FONTS + file))
pdfmetrics.registerFontFamily('Serif', normal='Serif', bold='Serif-B', italic='Serif-I', boldItalic='Serif-BI')

body = ParagraphStyle('body', fontName='Serif', fontSize=12, leading=18, alignment=TA_JUSTIFY, spaceAfter=8)
h2 = ParagraphStyle('h2', fontName='Serif-B', fontSize=14, leading=18, spaceBefore=10, spaceAfter=8)
h3 = ParagraphStyle('h3', fontName='Serif-B', fontSize=12, leading=16, spaceBefore=8, spaceAfter=6)
formula = ParagraphStyle('formula', parent=body, alignment=TA_CENTER, fontName='Serif-I', spaceBefore=2, spaceAfter=10)
quote = ParagraphStyle('quote', parent=body, fontSize=11, leading=15, leftIndent=0.4 * inch, rightIndent=0.4 * inch)
cell = ParagraphStyle('cell', fontName='Serif', fontSize=9.5, leading=11.5)
caption = ParagraphStyle('caption', fontName='Serif-B', fontSize=11, leading=14, spaceBefore=6, spaceAfter=6)
cell_num = ParagraphStyle('cellnum', parent=cell, alignment=2)


def inline(text):
    text = escape(text)
    text = re.sub(r'`([^`]+)`', r'<font name="Mono">\1</font>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)', r'<i>\1</i>', text)
    return text


def table(lines):
    rows = [[c.strip() for c in line.strip().strip('|').split('|')] for line in lines]
    align = rows.pop(1)
    right = [a.endswith(':') for a in align]
    data = [[Paragraph(inline(c), cell_num if right[i] and r else cell) for i, c in enumerate(row)]
            for r, row in enumerate(rows)]
    width = 6.5 * inch
    widths = None
    if len(rows[0]) == 7:
        widths = [0.4 * inch, 1.75 * inch] + [0.87 * inch] * 5
    elif len(rows[0]) == 6:
        widths = [0.85 * inch, 1.85 * inch, 0.75 * inch, 1.0 * inch, 0.95 * inch, 1.1 * inch]
    elif len(rows[0]) == 3:
        widths = [3.0 * inch, 2.5 * inch, 1.0 * inch]
    elif len(rows[0]) == 2:
        widths = [5.3 * inch, 1.2 * inch]
    t = Table(data, colWidths=widths or [width / len(rows[0])] * len(rows[0]), repeatRows=1)
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                           ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e6e6e6')),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    return t


def build(md):
    text = md.split('\n---\n', 1)[1]
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip() == '---':
            i += 1
        elif line.startswith('### '):
            out.append(Paragraph(inline(line[4:]), h3)); i += 1
        elif line.startswith('## '):
            out.append(Paragraph(inline(line[3:]), h2)); i += 1
        elif line.startswith('|'):
            block = []
            while i < len(lines) and lines[i].startswith('|'):
                block.append(lines[i]); i += 1
            pending = [out.pop()] if out and getattr(out[-1], 'style', None) is caption else []
            out.append(KeepTogether(pending + [table(block), Spacer(1, 10)]))
        elif line.startswith('> '):
            block = []
            while i < len(lines) and lines[i].startswith('>'):
                block.append(lines[i][1:].strip()); i += 1
            out.append(Paragraph(inline(' '.join(block)), quote))
        elif line.startswith('- '):
            items = []
            while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('  ') and lines[i].strip()):
                if lines[i].startswith('- '):
                    items.append(lines[i][2:].strip())
                else:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            out.append(ListFlowable([ListItem(Paragraph(inline(t), body), leftIndent=18) for t in items],
                                    bulletType='bullet', start='\u2022', leftIndent=18))
        elif line.startswith('  '):
            out.append(Paragraph(inline(line.strip()), formula)); i += 1
        else:
            block = []
            while (i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '|', '>', '- ', '  '))
                   and lines[i].strip() != '---'):
                block.append(lines[i].strip()); i += 1
            joined = ' '.join(block)
            out.append(Paragraph(inline(joined), caption if joined.startswith('**Table') else body))
    return out


if __name__ == '__main__':
    src, dest = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else 'RAGAS Evaluation of Bintanong'
    doc = SimpleDocTemplate(dest, pagesize=LETTER, leftMargin=inch, rightMargin=inch, topMargin=inch,
                            bottomMargin=inch, title=title, author='Bintanong research team')
    doc.build(build(open(src, encoding='utf-8').read()))
    print('wrote', dest)
