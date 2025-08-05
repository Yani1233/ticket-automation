# Makefile for Ticket Alert System

.PHONY: help install run test clean docker deploy

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run continuous monitoring"
	@echo "  make run-once   - Run single check"
	@echo "  make test       - Run all tests"
	@echo "  make test-email - Test email configuration"
	@echo "  make clean      - Clean temporary files"
	@echo "  make docker     - Build Docker image"

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -e .

run:
	./scripts/run.sh

run-once:
	./scripts/run.sh --once

test:
	. venv/bin/activate && python -m pytest tests/

test-email:
	./scripts/run.sh --test-email

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f state.json test_state.json simulation_state.json
	rm -rf logs/*.log

docker:
	docker build -t ticket-alert .