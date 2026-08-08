import io
from fpdf import FPDF
from app.models.order import Order

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "YCOMMERCE - PURCHASE RECEIPT", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generate_order_invoice(order: Order) -> io.BytesIO:
    """
    Generate order invoice: generates pdf invoice of users order
    """
    pdf = InvoicePDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Receipt N°: #{order.id:06d}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 10)
    fecha_str = order.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(order, "created_at") and order.created_at else "N/A"
    pdf.cell(0, 6, f"Emission Date: {fecha_str}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Payment status: {order.status} (By PayPal)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 8, "Product", border=1)
    pdf.cell(30, 8, "Quantity", border=1, align="C")
    pdf.cell(60, 8, "Total", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    calc_total = 0.0
    items_list = getattr(order, "items", []) or []
    for item in items_list:
        if hasattr(item, "product") and item.product and hasattr(item.product, "name"):
            product_name = item.product.name
        else:
            product_name = f"Producto ID {getattr(item, 'product_id', 'N/A')}"
        unit_price = getattr(item, "price", None)
        if unit_price is None and hasattr(item, "product") and item.product:
            unit_price = getattr(item.product, "price", 0.0)
        elif unit_price is None:
            unit_price = 0.0

        quantity = getattr(item, "quantity", 1)
        subtotal_item = quantity * float(unit_price)
        calc_total += subtotal_item

        pdf.cell(100, 8, str(product_name)[:45], border=1)
        pdf.cell(30, 8, str(quantity), border=1, align="C")
        pdf.cell(60, 8, f"${subtotal_item:.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    final_total = calc_total
    if final_total == 0.0:
        final_total = float(getattr(order, "total_amount", getattr(order, "total", getattr(order, "amount", 0.0))))

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(130, 8, "TOTAL PAID", border=1, align="R")
    pdf.cell(60, 8, f"${final_total:.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")    
    pdf_bytes = bytes(pdf.output())
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)
    
    return buffer