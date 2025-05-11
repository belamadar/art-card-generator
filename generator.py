import pandas as pd
import argparse
import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

# --------------------
# Helper: load data
# --------------------
def load_data(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    elif ext in ['.csv', '.xlsx']:
        if ext == '.csv':
            return pd.read_csv(path)
        else:
            return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

# --------------------
# Draw one card
# --------------------
def draw_card(c, x, y, data, styles):
    CARD_WIDTH, CARD_HEIGHT, padding = styles['CARD_WIDTH'], styles['CARD_HEIGHT'], styles['padding']
    # background
    c.setFillColor(styles['BACKGROUND_COLOR'])
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=3*mm, fill=1)
    # border
    c.setStrokeColor(styles['BORDER_COLOR'])
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=3*mm, fill=0)
    # title
    c.setFont(*styles['TITLE_FONT'])
    c.setFillColor(styles['BORDER_COLOR'])
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT - padding, data.get('namn', ''))
    # line
    line_y = y + CARD_HEIGHT - padding - 4
    c.setStrokeColor(styles['LINE_COLOR'])
    c.setLineWidth(0.5)
    c.line(x + padding, line_y, x + CARD_WIDTH - padding, line_y)
    # teknik
    c.setFont(*styles['TEXT_FONT'])
    c.setFillColor(colors.black)
    c.drawString(x + padding, line_y - 12, f"Teknik: {data.get('teknik', '')}")
    # storlek
    sz = data.get('storlek', '')
    if sz:
        c.drawString(x + padding, line_y - 25, f"Storlek: {sz}")
    # pris
    c.setFont(*styles['PRICE_FONT'])
    price_text = f"{data.get('pris', 0)} kr"
    w = c.stringWidth(price_text, *styles['PRICE_FONT'])
    c.drawString(x + CARD_WIDTH - padding - w, y + padding, price_text)

# --------------------
# Main: generate PDF
# --------------------
def create_cards(data_file, output_file):
    # page/card config
    PAGE_WIDTH, PAGE_HEIGHT = A4
    CARD_WIDTH = 85 * mm
    CARD_HEIGHT = 52.48 * mm
    padding = 6 * mm
    MARGIN_X = 10 * mm
    MARGIN_Y = 10 * mm
    cols = int((PAGE_WIDTH - 2*MARGIN_X)//CARD_WIDTH)
    rows = int((PAGE_HEIGHT - 2*MARGIN_Y)//CARD_HEIGHT)
    # styles
    styles = {
        'CARD_WIDTH': CARD_WIDTH,
        'CARD_HEIGHT': CARD_HEIGHT,
        'padding': padding,
        'BACKGROUND_COLOR': colors.HexColor('#fdfcfb'),
        'BORDER_COLOR': colors.HexColor('#a7988a'),
        'LINE_COLOR': colors.HexColor('#e3d5ca'),
        'TITLE_FONT': ('Helvetica-Bold', 14),
        'TEXT_FONT': ('Helvetica', 9),
        'PRICE_FONT': ('Helvetica-Oblique', 12)
    }
    # load
    df = load_data(data_file)
    # PDF
    c = canvas.Canvas(output_file, pagesize=A4)
    col = row = 0
    for _, row_data in df.iterrows():
        x = MARGIN_X + col*CARD_WIDTH
        y = PAGE_HEIGHT - MARGIN_Y - (row+1)*CARD_HEIGHT
        draw_card(c, x, y, row_data, styles)
        col += 1
        if col >= cols:
            col = 0
            row += 1
        if row >= rows:
            c.showPage()
            row = 0
    c.save()
    print(f"Created {output_file} with {len(df)} cards from {data_file}.")

# --------------------
# Entry: CLI args
# --------------------
if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Generate printable art cards from data file')
    p.add_argument('data_file', help='Input .json, .csv, or .xlsx file with keys namn, teknik, storlek, pris')
    p.add_argument('-o', '--output', default='kartkort.pdf', help='Output PDF filename')
    args = p.parse_args()
    create_cards(args.data_file, args.output)
