import os

files = [
    '/home/user/nhs-pipeline-task10/.github/workflows/ci.yml',
    '/home/user/nhs-pipeline-task10/.github/workflows/pr-checks.yml',
    '/home/user/nhs-pipeline-task10/.github/workflows/release.yml',
    '/home/user/nhs-pipeline-task10/.github/dependabot.yml',
    '/home/user/nhs-pipeline-task10/.github/PULL_REQUEST_TEMPLATE.md',
    '/home/user/nhs-pipeline-task10/scripts/generate_ci_seeds.py',
    '/home/user/nhs-pipeline-task10/CHANGELOG.md',
    '/home/user/nhs-pipeline-task10/CONTRIBUTING.md',
]

for f in files:
    size = os.path.getsize(f)
    print(f"✅ {f.split('task10/')[-1]} ({size} bytes)")