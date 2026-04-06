import subprocess

commands = [
    'ALTER TABLE lab_report ADD COLUMN published_by BIGINT',
    'ALTER TABLE lab_report ADD COLUMN published_time DATETIME',
    "ALTER TABLE lab_report MODIFY COLUMN patient_id BIGINT",
    "ALTER TABLE lab_report MODIFY COLUMN patient_name VARCHAR(50)",
    "ALTER TABLE lab_report MODIFY COLUMN test_items VARCHAR(200)",
]

for sql in commands:
    result = subprocess.run(
        ['mysql', '-u', 'root', '-p1234', 'lab_management', '-e', sql],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f'[OK] {sql}')
    elif 'Duplicate column' in result.stderr:
        print(f'[SKIP] {sql}')
    else:
        print(f'[ERROR] {sql} -> {result.stderr.strip()}')

# Verify
verify = subprocess.run(
    ['mysql', '-u', 'root', '-p1234', 'lab_management', '-e',
     "SELECT COUNT(*) AS cols FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='lab_management' AND TABLE_NAME='lab_report'"],
    capture_output=True, text=True
)
print(f'\nlab_report total columns: {verify.stdout.strip()}')
