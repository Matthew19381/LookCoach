from .local_llm import LocalLLMService


class ExplainableAI:
    def __init__(self):
        self.llm = LocalLLMService()

    def quick_summary(self, recommendation: dict) -> str:
        name = recommendation.get("name", "")
        effect = recommendation.get("effect_size", 0)
        time = recommendation.get("time_to_effect", 0)
        evidence = recommendation.get("evidence_level", "")
        return f"{name}: {effect*100:.0f}% effectiveness in {time} weeks (evidence: {evidence})"

    def deep_dive_lesson(self, recommendation: dict) -> str:
        prompt = f"""Explain in detail why "{recommendation.get('name', '')}" is recommended:
- What does it do?
- Why is it effective (effect size: {recommendation.get('effect_size', 0)})?
- How long until results ({recommendation.get('time_to_effect', 0)} weeks)?
- Evidence level: {recommendation.get('evidence_level', '')}
- Any contraindications: {recommendation.get('contraindications', 'none')}

Provide a mini-lesson (2-3 paragraphs) teaching the user about this recommendation."""
        try:
            return self.llm.generate_text(prompt)
        except Exception:
            name = recommendation.get("name", "this recommendation")
            effect = recommendation.get("effect_size", 0) * 100
            time = recommendation.get("time_to_effect", 0)
            return f"{name} is recommended for its {effect:.0f}% effectiveness within {time} weeks. Consistent application is key to seeing results. Consult skincare or fitness professionals for personalized advice."
