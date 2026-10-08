from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from database.db import get_assessment_by_id, insert_assessment
from services.assessment_service import construir_avaliacao
from services.risk_calculation import CONTEXTUAL_RULES, identificar_fatores

assessment_bp = Blueprint('assessment', __name__)


def validate_assessment_form(form_data: dict[str, str]) -> list[str]:
    """Validate inputs before starting the analysis pipeline."""
    errors: list[str] = []
    required_fields = {
        'course': 'Curso',
        'semester': 'Semestre',
        'academic_workload': 'Carga acadêmica',
        'difficulty': 'Dificuldade',
        'satisfaction': 'Satisfação',
        'motivation': 'Motivação',
        'text_response': 'Resposta textual',
    }
    for field, label in required_fields.items():
        if not form_data.get(field, '').strip():
            errors.append(f'O campo "{label}" é obrigatório.')

    if form_data.get('course') and form_data['course'] not in current_app.config['COURSES']:
        errors.append('Selecione um curso válido.')
    try:
        semester = int(form_data.get('semester', ''))
        if semester not in current_app.config['SEMESTERS']:
            errors.append('Selecione um semestre entre 1º e 10º.')
    except ValueError:
        if form_data.get('semester'):
            errors.append('O semestre deve ser numérico.')

    for field, rules in CONTEXTUAL_RULES.items():
        if form_data.get(field) and form_data[field] not in rules:
            errors.append(f'Resposta inválida para "{field}".')

    text = form_data.get('text_response', '').strip()
    if text and len(text) < 10:
        errors.append('A resposta textual deve ter pelo menos 10 caracteres.')
    if len(text) > current_app.config['MAX_TEXT_LENGTH']:
        errors.append(
            f'A resposta textual deve ter no máximo {current_app.config["MAX_TEXT_LENGTH"]} caracteres.'
        )
    return errors


@assessment_bp.route('/nova-avaliacao', methods=['GET', 'POST'])
def new_assessment():
    form_data = request.form.to_dict() if request.method == 'POST' else {}
    errors: list[str] = []

    if request.method == 'POST':
        errors = validate_assessment_form(form_data)
        if not errors:
            assessment = construir_avaliacao(
                form_data,
                limiares=current_app.config['LIMIAR_DE_RISCO'],
            )
            assessment_id = insert_assessment(current_app.config['DATABASE_PATH'], assessment)
            return redirect(url_for('assessment.result', assessment_id=assessment_id))
        flash('Revise os campos destacados antes de analisar a avaliação.', 'danger')

    return render_template(
        'new_assessment.html',
        courses=current_app.config['COURSES'],
        semesters=current_app.config['SEMESTERS'],
        form_data=form_data,
        errors=errors,
    )


@assessment_bp.route('/resultado/<int:assessment_id>')
def result(assessment_id: int):
    assessment = get_assessment_by_id(current_app.config['DATABASE_PATH'], assessment_id)
    if assessment is None:
        abort(404)
    contextual_components = {
        field: CONTEXTUAL_RULES[field][getattr(assessment, field)]
        for field in CONTEXTUAL_RULES
    }
    factors = identificar_fatores(contextual_components, assessment.text_polarity)
    return render_template('result.html', assessment=assessment, factors=factors)


@assessment_bp.route('/avaliacoes/<int:assessment_id>')
def detail(assessment_id: int):
    assessment = get_assessment_by_id(current_app.config['DATABASE_PATH'], assessment_id)
    if assessment is None:
        abort(404)
    contextual_components = {
        field: CONTEXTUAL_RULES[field][getattr(assessment, field)]
        for field in CONTEXTUAL_RULES
    }
    factors = identificar_fatores(contextual_components, assessment.text_polarity)
    return render_template('assessment_detail.html', assessment=assessment, factors=factors)
