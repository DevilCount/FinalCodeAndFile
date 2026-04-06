import subprocess
import sys

sql_commands = [
    'ALTER TABLE lab_report ADD COLUMN ai_confidence INT',
    'ALTER TABLE lab_report ADD COLUMN ai_model_version VARCHAR(50)',
    'ALTER TABLE lab_report ADD COLUMN ai_diagnosis_time DATETIME',
    'ALTER TABLE lab_report ADD COLUMN technical_reviewer_id BIGINT',
    'ALTER TABLE lab_report ADD COLUMN technical_reviewer_name VARCHAR(50)',
    'ALTER TABLE lab_report ADD COLUMN technical_review_time DATETIME',
    'ALTER TABLE lab_report ADD COLUMN technical_review_result VARCHAR(20)',
    'ALTER TABLE lab_report ADD COLUMN technical_review_comment VARCHAR(500)',
    'ALTER TABLE lab_report ADD COLUMN clinical_reviewer_id BIGINT',
    'ALTER TABLE lab_report ADD COLUMN clinical_reviewer_name VARCHAR(50)',
    'ALTER TABLE lab_report ADD COLUMN clinical_review_time DATETIME',
    'ALTER TABLE lab_report ADD COLUMN clinical_review_result VARCHAR(20)',
    'ALTER TABLE lab_report ADD COLUMN clinical_review_comment VARCHAR(500)',
    'ALTER TABLE lab_report ADD COLUMN abnormal_indicator_count INT DEFAULT 0',
    'ALTER TABLE lab_report ADD COLUMN critical_indicator_count INT DEFAULT 0',
    'ALTER TABLE lab_report ADD COLUMN revoked_by BIGINT',
    'ALTER TABLE lab_report ADD COLUMN revoked_by_name VARCHAR(50)',
    'ALTER TABLE lab_report ADD COLUMN revoked_time DATETIME',
    'ALTER TABLE lab_report ADD COLUMN revoked_reason VARCHAR(500)',
    'ALTER TABLE lab_report ADD COLUMN archived_by BIGINT',
    'ALTER TABLE lab_report ADD COLUMN archived_by_name VARCHAR(50)',
    'ALTER TABLE lab_report ADD COLUMN archived_time DATETIME',
    'ALTER TABLE lab_report ADD COLUMN print_count INT DEFAULT 0',
    'ALTER TABLE lab_report ADD COLUMN print_time DATETIME',
    'ALTER TABLE lab_report ADD COLUMN published_by_name VARCHAR(50)',
]

success_count = 0
skip_count = 0
error_count = 0

for sql in sql_commands:
    result = subprocess.run(
        ['mysql', '-u', 'root', '-p1234', 'lab_management', '-e', sql],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f'[OK] {sql}')
        success_count += 1
    elif 'Duplicate column' in result.stderr:
        print(f'[SKIP] {sql} (already exists)')
        skip_count += 1
    else:
        print(f'[ERROR] {sql}')
        print(f'  -> {result.stderr.strip()}')
        error_count += 1

print(f'\n=== Migration Summary ===')
print(f'Success: {success_count}')
print(f'Skipped (exists): {skip_count}')
print(f'Errors: {error_count}')

# Verify column count
verify_sql = "SELECT COUNT(*) AS total_columns FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='lab_management' AND TABLE_NAME='lab_report'"
result = subprocess.run(
    ['mysql', '-u', 'root', '-p1234', 'lab_management', '-e', verify_sql],
    capture_output=True, text=True
)
print(f'\nlab_report total columns: {result.stdout.strip()}')
