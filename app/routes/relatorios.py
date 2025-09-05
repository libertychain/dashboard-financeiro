from flask import Blueprint, request, jsonify, session, send_file
from app.services.pdf_service import PDFReportService
from app.services.export_service import ExportService
import io

relatorios = Blueprint('relatorios', __name__)

@relatorios.route('/api/relatorios/pdf', methods=['POST'])
def gerar_relatorio_pdf():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    mes = data.get('mes')
    ano = data.get('ano')
    
    if not all([mes, ano]):
        return jsonify({'error': 'Mês e ano são obrigatórios'}), 400
    
    pdf_service = PDFReportService()
    buffer = pdf_service.gerar_relatorio_mensal(session['user_id'], mes, ano)
    
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'relatorio_{mes}_{ano}.pdf'
    )

@relatorios.route('/api/exportar', methods=['POST'])
def exportar_dados():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    formato = data.get('formato', 'csv')
    tipo = data.get('tipo', 'todos')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    export_service = ExportService()
    
    if formato == 'csv':
        content = export_service.exportar_csv(
            session['user_id'], tipo, start_date, end_date
        )
        if content:
            buffer = io.StringIO(content)
            return send_file(
                io.BytesIO(buffer.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'dados_{session["user_id"]}.csv'
            )
    
    elif formato == 'excel':
        buffer = export_service.exportar_excel(
            session['user_id'], tipo, start_date, end_date
        )
        if buffer:
            return send_file(
                buffer,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'dados_{session["user_id"]}.xlsx'
            )
    
    elif formato == 'json':
        content = export_service.exportar_json(
            session['user_id'], tipo, start_date, end_date
        )
        if content:
            buffer = io.StringIO(content)
            return send_file(
                io.BytesIO(buffer.getvalue().encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'dados_{session["user_id"]}.json'
            )
    
    return jsonify({'error': 'Erro ao exportar dados'}), 500
