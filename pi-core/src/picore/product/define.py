"""
Convert ProblemStatement to ProductSpec for template_pack only.
Fail if required fields are missing.
"""
from typing import List
from ..models.core import ProblemStatement, ProductSpec, ProductType

class ProductDefiner:
    @staticmethod
    def define(problem: ProblemStatement) -> ProductSpec:
        if not (problem.title and problem.summary and problem.problem_id):
            raise RuntimeError("ProblemStatement missing required fields.")
        deliverables = [
            "README.md",
            "LICENSE.txt",
            "templates/base_template.md",
            "templates/advanced_template.md",
            "examples/filled_example.md",
            "docs/usage.md",
            "docs/customization.md",
            "listing.md"
        ]
        return ProductSpec(
            product_id=problem.problem_id,
            problem_id=problem.problem_id,
            product_type=ProductType.template_pack,
            target_user=problem.who_is_hurt or "User",
            value_prop=problem.summary,
            deliverables=deliverables,
            non_goals=["Not a full SaaS product", "No code generation"],
            constraints=["Offline use", "Markdown only"],
            acceptance_criteria=[
                "All deliverables present",
                "README explains usage",
                "Templates are clear and customizable"
            ]
        )
