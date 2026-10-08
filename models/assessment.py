import json
from dataclasses import dataclass
from typing import Any


@dataclass
class Assessment:
    """Represents a reproducible computational academic assessment."""

    course: str
    semester: int
    academic_workload: str
    difficulty: str
    satisfaction: str
    motivation: str
    text_response: str
    text_polarity: str
    text_score: int
    positive_terms: list[str]
    negative_terms: list[str]
    contextual_score: int
    total_score: int
    risk_level: str
    expected_risk: str | None = None
    is_simulated: bool = False
    created_at: str | None = None
    id: int | None = None

    @classmethod
    def from_row(cls, row: Any) -> 'Assessment':
        data = dict(row)
        return cls(
            id=data['id'],
            course=data['course'],
            semester=int(data['semester']),
            academic_workload=data['academic_workload'],
            difficulty=data['difficulty'],
            satisfaction=data['satisfaction'],
            motivation=data['motivation'],
            text_response=data['text_response'],
            text_polarity=data['text_polarity'],
            text_score=int(data['text_score']),
            positive_terms=json.loads(data['positive_terms'] or '[]'),
            negative_terms=json.loads(data['negative_terms'] or '[]'),
            contextual_score=int(data['contextual_score']),
            total_score=int(data['total_score']),
            risk_level=data['risk_level'],
            expected_risk=data['expected_risk'],
            is_simulated=bool(data['is_simulated']),
            created_at=data['created_at'],
        )

    @property
    def polarity_label(self) -> str:
        return {'positive': 'Positiva', 'neutral': 'Neutra', 'negative': 'Negativa'}[self.text_polarity]

    @property
    def formatted_date(self) -> str:
        if not self.created_at:
            return '—'
        return self.created_at.replace(' UTC', ' UTC')

    def to_database_params(self, created_at: str) -> dict[str, Any]:
        return {
            'course': self.course,
            'semester': self.semester,
            'academic_workload': self.academic_workload,
            'difficulty': self.difficulty,
            'satisfaction': self.satisfaction,
            'motivation': self.motivation,
            'text_response': self.text_response,
            'text_polarity': self.text_polarity,
            'text_score': self.text_score,
            'positive_terms': json.dumps(self.positive_terms, ensure_ascii=False),
            'negative_terms': json.dumps(self.negative_terms, ensure_ascii=False),
            'contextual_score': self.contextual_score,
            'total_score': self.total_score,
            'risk_level': self.risk_level,
            'expected_risk': self.expected_risk,
            'is_simulated': int(self.is_simulated),
            'created_at': created_at,
        }
