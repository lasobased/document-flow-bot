#!/bin/bash

# Git Setup Script for Document Flow Bot
# Инициализирует Git репозиторий и делает первые коммиты

echo "================================================"
echo "Git Repository Initialization Script"
echo "================================================"

# Проверка что мы в правильной директории
if [ ! -f "README.md" ]; then
    echo "ERROR: README.md not found. Please run this script from project root."
    exit 1
fi

echo ""
echo "[1/6] Initializing Git repository..."
git init

echo ""
echo "[2/6] Adding all files to staging..."
git add .

echo ""
echo "[3/6] Creating initial commit..."
git commit -m "Initial commit: Document Flow Bot - Rule-Based Validation System

- Project structure setup
- README.md with full description
- Architecture documentation (UML diagrams)
- .gitignore configuration
- requirements.txt with dependencies"

echo ""
echo "[4/6] Creating commit for data layer..."
git add data/raw/rules.json
git commit -m "Add Knowledge Base: rules.json

- Document validation rules
- Thresholds and limits
- INN validation settings
- Required fields per document type
- Critical rules configuration
- Validation messages"

echo ""
echo "[5/6] Creating commit for business logic..."
git add src/logic.py src/validators.py src/mock_data.py
git commit -m "Add Rule-Based Logic and Validators

Implemented:
- Inference Engine (logic.py)
- 3 Critical Filters (Hard Filters)
- 4 Hard Validations
- 2 Soft Validations (Warnings)
- Individual validators (validators.py)
- 9 test cases (mock_data.py)

Features:
- Date validation
- INN validation
- Amount range checking
- Required fields validation
- Document type validation"

echo ""
echo "[6/6] Creating commit for UI and tests..."
git add src/main.py tests/test_validation.py
git commit -m "Add Streamlit UI and Unit Tests

UI Features:
- 3 working modes (Custom Input, Test Cases, Batch)
- Interactive forms for document input
- Real-time validation
- Color-coded results (Success/Warning/Error)
- Detailed validation reports

Tests:
- 40+ unit tests
- Validator tests
- Integration tests
- Test coverage for all validation rules"

echo ""
echo "================================================"
echo "Git repository successfully initialized!"
echo "================================================"
echo ""
echo "Repository status:"
git status

echo ""
echo "Commit history:"
git log --oneline

echo ""
echo "Next steps:"
echo "1. Create a repository on GitHub"
echo "2. Run: git remote add origin <your-github-url>"
echo "3. Run: git branch -M main"
echo "4. Run: git push -u origin main"
echo ""
echo "================================================"
