import csv
from io import StringIO

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, url_for

from database.db import (
    RISK_LEVELS,
    get_dashboard_metrics,
    get_distinct_courses,
    get_validation_assessments,
    list_assessments,
)
from services.simulated_data import SIMULATED_DATA_NOTICE, carregar_dados_simulados


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/historico')
def history():
    filters = {
        'search': request.args.get('search', ''),
        'course': request.args.get('course', ''),
        'semester': request.args.get('semester', ''),
        'risk_level': request.args.get('risk_level', ''),
    }
    assessments = list_assessments(current_app.config['DATABASE_PATH'], filters)
    return render_template(
        'history.html',
        assessments=assessments,
        filters=filters,
        courses=get_distinct_courses(current_app.config['DATABASE_PATH']),
        semesters=current_app.config['SEMESTERS'],
        risk_levels=RISK_LEVELS,
    )


@dashboard_bp.route('/dados-simulados')
def simulated_data():
    database_path = current_app.config['DATABASE_PATH']
    assessments = list_assessments(database_path, {'simulated_only': '1'}, limit=20)
    metrics = get_dashboard_metrics(database_path)
    return render_template(
        'simulated_data.html',
        assessments=assessments,
        simulated_total=metrics['simulated_total'],
        notice=SIMULATED_DATA_NOTICE,
    )


@dashboard_bp.route('/dados-simulados/recarregar', methods=['POST'])
def reload_simulated_data():
    result = carregar_dados_simulados(
        current_app.config['DATABASE_PATH'],
        current_app.config['SIMULATED_DATA_PATH'],
        replace_simulated=True,
    )
    flash(
        f'{result["created"]} dados simulados foram carregados; {result["deleted"]} registros sintéticos anteriores foram substituídos.',
        'success',
    )
    return redirect(url_for('dashboard.simulated_data'))


@dashboard_bp.route('/validacao')
def validation():
    assessments = get_validation_assessments(current_app.config['DATABASE_PATH'])
    confusion = {expected: {produced: 0 for produced in RISK_LEVELS} for expected in RISK_LEVELS}
    correct = 0
    rows = []
    for assessment in assessments:
        expected = assessment.expected_risk or 'Não informado'
        produced = assessment.risk_level
        is_correct = expected == produced
        correct += int(is_correct)
        if expected in confusion and produced in confusion[expected]:
            confusion[expected][produced] += 1
        rows.append({'assessment': assessment, 'is_correct': is_correct})

    total = len(assessments)
    errors = total - correct
    accuracy = round((correct / total) * 100, 2) if total else 0.0
    return render_template(
        'validation.html',
        rows=rows,
        total=total,
        correct=correct,
        errors=errors,
        accuracy=accuracy,
        confusion=confusion,
        risk_levels=RISK_LEVELS,
    )


@dashboard_bp.route('/relatorios')
def reports():
    metrics = get_dashboard_metrics(current_app.config['DATABASE_PATH'])
    validation_assessments = get_validation_assessments(current_app.config['DATABASE_PATH'])
    correct = sum(item.expected_risk == item.risk_level for item in validation_assessments)
    validation_total = len(validation_assessments)
    accuracy = round((correct / validation_total) * 100, 2) if validation_total else 0.0
    return render_template(
        'reports.html',
        metrics=metrics,
        validation_total=validation_total,
        validation_accuracy=accuracy,
    )


@dashboard_bp.route('/relatorios/exportar-csv')
def export_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'course', 'semester', 'academic_workload', 'difficulty', 'satisfaction',
        'motivation', 'text_response', 'text_polarity', 'text_score', 'contextual_score',
        'total_score', 'risk_level', 'expected_risk', 'is_simulated', 'created_at',
    ])
    for item in list_assessments(current_app.config['DATABASE_PATH']):
        writer.writerow([
            item.id, item.course, item.semester, item.academic_workload, item.difficulty,
            item.satisfaction, item.motivation, item.text_response, item.text_polarity,
            item.text_score, item.contextual_score, item.total_score, item.risk_level,
            item.expected_risk or '', int(item.is_simulated), item.created_at,
        ])
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=relatorio_avaliacoes.csv'},
    )
