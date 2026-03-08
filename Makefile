.PHONY: test lint health sprint-report

test:
	pytest

lint:
	ruff check .
	mypy .
	bandit -r . -ll

health:
	@echo "Running repo health check (placeholder)"
	@python3 -c "print('Health check passed.')"

sprint-report:
	@echo "Generating sprint report (placeholder)"
	@python3 -c "print('Sprint report generated.')"
