from app import app
from flask import url_for

print(sorted({rule.endpoint: rule.rule for rule in app.url_map.iter_rules()}.items()))
with app.test_request_context():
    print('build:', url_for('track_request', reference_number='BC-20240730-001'))
