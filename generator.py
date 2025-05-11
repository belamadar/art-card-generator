import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
import json
import os

# Configuration: card size (85mm x 52.48mm) and layout
PAGE_WIDTH, PAGE_HEIGHT = A4
CARD_WIDTH = 85 * mm
CARD_HEIGHT = 52.48 * mm
MARGIN_X = 10 * mm
MARGIN_Y = 10 * mm
COLUMNS = int((PAGE_WIDTH - 2 * MARGIN_X) // CARD_WIDTH)
ROWS = int((PAGE_HEIGHT - 2 * MARGIN_Y) // CARD_HEIGHT)

# Styling
BACKGROUND_COLOR = colors.HexColor('#fdfcfb')  # subtle cream
BORDER_COLOR = colors.HexColor('#a7988a')     # soft taupe
TITLE_FONT = ('Helvetica-Bold', 14)
TEXT_FONT = ('Helvetica', 9)
PRICE_FONT = ('Helvetica-Oblique', 12)
LINE_COLOR = colors.HexColor('#e3d5ca')

# File paths: support JSON or CSV with Swedish keys
data_file = 'målningar.json'  # or 'målningar.csv'
pdf_file = 'kartkort.pdf'

# Read data
ext = os.path.splitext(data_file)[1].lower()
if ext == '.json':
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
elif ext == '.csv':
    df = pd.read_csv(data_file)
else:
    raise ValueError('Felaktigt filformat: ' + ext)

# Create PDF
c = canvas.Canvas(pdf_file, pagesize=A4)

def draw_card(x, y, data):
    # Background and border
    c.setFillColor(BACKGROUND_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=3*mm, fill=1, stroke=0)
    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=3*mm, fill=0, stroke=1)

    padding = 6 * mm
    # Title (Namn)
    c.setFont(*TITLE_FONT)
    c.setFillColor(BORDER_COLOR)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT - padding, data.get('namn', ''))
    # Separator line
    c.setStrokeColor(LINE_COLOR)
    c.setLineWidth(0.5)
    line_y = y + CARD_HEIGHT - padding - 4
    c.line(x + padding, line_y, x + CARD_WIDTH - padding, line_y)

    # Technique (Teknik)
    c.setFont(*TEXT_FONT)
    c.setFillColor(colors.black)
    teknikt = f"Teknik: {data.get('teknik', '')}"
    c.drawString(x + padding, line_y - 12, teknikt)

    # Price (Pris)
    c.setFont(*PRICE_FONT)
    pris = data.get('pris', 0)
    price_text = f"{pris} kr"
    text_width = c.stringWidth(price_text, *PRICE_FONT)
    c.drawString(x + CARD_WIDTH - padding - text_width, y + padding, price_text)

# Loop through paintings and place cards
col = row = 0
for _, row_data in df.iterrows():
    x = MARGIN_X + col * CARD_WIDTH
    y = PAGE_HEIGHT - MARGIN_Y - (row + 1) * CARD_HEIGHT
    draw_card(x, y, row_data)
    col += 1
    if col >= COLUMNS:
        col = 0
        row += 1
    if row >= ROWS:
        c.showPage()
        row = 0

# Save PDF
c.save()
print(f"Skapade {pdf_file} med {len(df)} kort.")
