def format_currency(value):
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_date(date_str):
    """Formata data para formato brasileiro"""
    from datetime import datetime
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    return date_str
