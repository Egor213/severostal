#!/bin/bash
set -e

# --------- parse args ---------
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --project-root) PROJECT_ROOT="$2"; shift ;;
        --tests-dir) TESTS_DIR="$2"; shift ;;
        --config-path) CONFIG_PATH="$2"; shift ;;
        --model) MODEL="$2"; shift ;;
        --temperature) TEMPERATURE="$2"; shift ;;
        --max-generate-retries) MAX_GEN_RETRIES="$2"; shift ;;
        --max-fix-attempts) MAX_FIX_ATTEMPTS="$2"; shift ;;
        --target-line-coverage) TARGET_COV="$2"; shift ;;
        --max-async-workers) MAX_WORKERS="$2"; shift ;;
        --target-dir) TARGET_DIR="$2"; shift ;;
        --target-file) TARGET_FILE="$2"; shift ;;
        --target-class) TARGET_CLASS="$2"; shift ;;
        --target-function) TARGET_FUNCTION="$2"; shift ;;
        --pr-mode) PR_MODE="$2"; shift ;;
        --base-branch) BASE_BRANCH="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# --------- resolve paths ---------
WORKDIR="${GITHUB_WORKSPACE:-$PWD}"
ABS_PROJECT_ROOT="$WORKDIR/$PROJECT_ROOT"
REPORT_DIR="$ABS_PROJECT_ROOT/test_analysis_report"

echo "=== Generator Tests ==="
echo "Project root: $ABS_PROJECT_ROOT"
echo "Tests dir:    $TESTS_DIR"
echo "Config:       $CONFIG_PATH"

# --------- создаём .env если нужен ---------
ENV_FILE="$ABS_PROJECT_ROOT/config/.env"
mkdir -p "$(dirname "$ENV_FILE")"
if [ -n "$AI_API_KEY" ]; then
    echo "ai_api_key=$AI_API_KEY" > "$ENV_FILE"
fi

# --------- собираем CLI-аргументы ---------
CLI_ARGS=(
    --project "$ABS_PROJECT_ROOT"
    --config "$ABS_PROJECT_ROOT/$CONFIG_PATH"
    --tests-dir "$TESTS_DIR"
    --max-generate-retries "$MAX_GEN_RETRIES"
    --max-fix-attempts "$MAX_FIX_ATTEMPTS"
    --target_line_coverage "$TARGET_COV"
    --max_async_workers "$MAX_WORKERS"
)

[ -n "$MODEL" ]           && CLI_ARGS+=(--model "$MODEL")
[ -n "$TEMPERATURE" ]     && CLI_ARGS+=(--temperature "$TEMPERATURE")
[ -n "$TARGET_DIR" ]      && CLI_ARGS+=(--target-dir "$TARGET_DIR")
[ -n "$TARGET_FILE" ]     && CLI_ARGS+=(--target-file "$TARGET_FILE")
[ -n "$TARGET_CLASS" ]    && CLI_ARGS+=(--target-class "$TARGET_CLASS")
[ -n "$TARGET_FUNCTION" ] && CLI_ARGS+=(--target-function "$TARGET_FUNCTION")

# --------- запуск ---------
cd "$ABS_PROJECT_ROOT"
echo "Running: python -m src.app.app ${CLI_ARGS[@]}"
python -m src.app.app "${CLI_ARGS[@]}"

# --------- PR creation ---------
if [ "$PR_MODE" != "true" ]; then
    echo "PR mode disabled, skipping commit."
    exit 0
fi

cd "$WORKDIR"

# Настройка git
git config --global user.email "generator-tests-bot@users.noreply.github.com"
git config --global user.name  "Generator Tests Bot"

if [ -z "$(git status --porcelain)" ]; then
    echo "No changes generated, exiting."
    exit 0
fi

TIMESTAMP=$(date +%s)
BRANCH_NAME="generator-tests/${PR_NUMBER:-manual}-${TIMESTAMP}"

# PR body
REPORT_HTML="$REPORT_DIR/index.html"
if [ -f "$REPORT_HTML" ]; then
    REPORT_NOTE="📊 HTML-отчёт приложен в артефактах workflow"
else
    REPORT_NOTE="Отчёт не создан"
fi

PR_BODY=$(cat <<EOF
## 🤖 Автоматически сгенерированные тесты

Эти тесты были сгенерированы с помощью **Generator_Tests** LLM-пайплайна.

### Параметры запуска
- Модель: \`${MODEL:-из конфига}\`
- Целевое покрытие: \`${TARGET_COV}%\`
- Макс. попыток генерации: \`${MAX_GEN_RETRIES}\`
- Макс. попыток починки: \`${MAX_FIX_ATTEMPTS}\`

### Что сделано
- ✅ Сгенерированы unit-тесты для непокрытых функций
- ✅ Каждый тест прошёл валидацию в sandbox
- ✅ Проведён анализ покрытия + мутационное тестирование
- ✅ Удалены дубликаты и неиспользуемые импорты

${REPORT_NOTE}

---
*PR создан: $(date)*
EOF
)

git checkout -b "$BRANCH_NAME"
git add "$PROJECT_ROOT/$TESTS_DIR"
# не коммитим служебные файлы
git reset -- "*.log" "*.db" "*.json" "*.xml" "**/test_analysis_report/**" "**/.coverage*"

if [ -z "$(git diff --cached --name-only)" ]; then
    echo "Only report/log files changed, skipping PR."
    exit 0
fi

git commit -m "🤖 Add generated tests (coverage ${TARGET_COV}%)"
git push origin "$BRANCH_NAME"

# создаём PR
PR_TARGET_BRANCH="${PR_REF:-$BASE_BRANCH}"
gh pr create \
    --base "$PR_TARGET_BRANCH" \
    --head "$BRANCH_NAME" \
    --title "🤖 Generator Tests: новые тесты (${TIMESTAMP})" \
    --body "$PR_BODY"

echo "✅ PR создан: $BRANCH_NAME → $PR_TARGET_BRANCH"
