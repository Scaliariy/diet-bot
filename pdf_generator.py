from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(diet, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    # Content
    content = []

    # Header
    content.append(Paragraph("<b>Diet Plan</b>", styles['Heading1']))
    content.append(Spacer(1, 12))
    content.append(
        Paragraph("<b>Total Price:</b> {} {}".format(diet['total_price'], diet['currency']), styles['Normal']))
    content.append(Spacer(1, 12))

    # Meals
    for meal in diet['meals']:
        content.append(
            Paragraph("<b>Meal {}: {}</b>".format(meal['meal_number'], meal['description']), styles['Heading2']))
        content.append(Spacer(1, 6))
        for dish in meal['dishes']:
            content.append(Paragraph("<i>Dish:</i> {}".format(dish['name']), styles['Normal']))
            content.append(Paragraph("<i>Ingredients:</i> {}".format(", ".join(dish['ingredients'])), styles['Normal']))
            content.append(
                Paragraph("<i>Cooking Instructions:</i> {}".format(dish['cooking_instructions']), styles['Normal']))
            content.append(Paragraph("<i>Price:</i> {} {}".format(dish['price'], diet['currency']), styles['Normal']))
            content.append(Spacer(1, 6))
        content.append(
            Paragraph("<b>Total Price:</b> {} {}".format(meal['total_price'], diet['currency']), styles['Normal']))
        content.append(Spacer(1, 12))

    doc.build(content)
