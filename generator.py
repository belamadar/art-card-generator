#!/usr/bin/env python3

import pandas as pd
import argparse
import json
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

# --------------------
# Setup font
# --------------------
pdfmetrics.registerFont(TTFont('LibreBaskerville', 'LibreBaskerville-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LibreBaskerville-Bold', 'LibreBaskerville-Bold.ttf'))

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
        raise ValueError(f"Filformat som inte stöds: {ext}")

# --------------------
# Draw one card
# --------------------
def draw_card(c, x, y, data, styles):
    CARD_WIDTH, CARD_HEIGHT, padding = styles['CARD_WIDTH'], styles['CARD_HEIGHT'], styles['padding']

    # Background
    c.setFillColor(colors.white)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)

    # Border (cutting guide)
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, fill=0, stroke=1)

    # Title (name, uppercase and left-aligned)
    c.setFont('LibreBaskerville-Bold', 14)
    c.setFillColor(colors.black)
    namn = data.get('namn', '').upper()
    c.drawString(x + padding, y + CARD_HEIGHT - padding - 14, namn)

    # Information
    c.setFont('LibreBaskerville', 10)
    teknik = data.get('teknik', '')
    storlek = data.get('storlek', '')
    datum = data.get('datum', '')
    line1 = "Teknik:"
    line2 = "Storlek:"
    c.drawString(x + padding, y + CARD_HEIGHT - padding - 40, line1)
    c.drawString(x + padding, y + CARD_HEIGHT - padding - 55, line2)
    c.setFont('LibreBaskerville-Bold', 11)
    c.drawString(x + 25 * mm, y + CARD_HEIGHT - padding - 40, teknik)
    c.drawString(x + 25 * mm, y + CARD_HEIGHT - padding - 55, storlek)

    # Pris
    # c.setFont('LibreBaskerville', 11)
    # c.drawString(x + padding, y + CARD_HEIGHT - padding - 40, "Pris:")
    c.setFont('LibreBaskerville-Bold', 11)
    c.drawRightString(x + CARD_WIDTH - padding, y + padding - 5, f"{data.get('pris', 0)} kr")

    # Konstnär
    konstnar = data.get('konstnär', '')
    if konstnar:
        # c.setFont('LibreBaskerville', 11)
        # c.drawString(x + padding, y + padding + 5, "Konstnär:")
        c.setFont('LibreBaskerville-Bold', 11)
        c.drawString(x + padding, y + padding - 5, konstnar)

# --------------------
# Main: generate PDF
# --------------------
def create_cards(data_file, output_file):
    PAGE_WIDTH, PAGE_HEIGHT = A4
    CARD_WIDTH = 85 * mm
    CARD_HEIGHT = 52.48 * mm
    padding = 10 * mm
    MARGIN_X = 10 * mm
    MARGIN_Y = 10 * mm
    cols = int((PAGE_WIDTH - 2*MARGIN_X)//CARD_WIDTH)
    rows = int((PAGE_HEIGHT - 2*MARGIN_Y)//CARD_HEIGHT)

    styles = {
        'CARD_WIDTH': CARD_WIDTH,
        'CARD_HEIGHT': CARD_HEIGHT,
        'padding': padding,
    }

    df = load_data(data_file)
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
    print(f"Skapade {output_file} med {len(df)} kort från {data_file}.")

# --------------------
# Entry: CLI args
# --------------------
if __name__ == '__main__':
    import sys
    default_input = 'målningar.csv'
    default_output = 'kartkort.pdf'

    if len(sys.argv) == 1:
        # No arguments: use defaults
        print(f"Inga argument angivna. Använder {default_input}.")
        create_cards(default_input, default_output)
    else:
        # Use argparse as usual
        p = argparse.ArgumentParser(description='Generate printable art cards from data file')
        p.add_argument('data_file', help='Input .json, .csv, or .xlsx file with keys namn, teknik, storlek, pris, konstnär')
        p.add_argument('-o', '--output', default='kartkort.pdf', help='Output PDF filename')
        args = p.parse_args()
        create_cards(args.data_file, args.output)

