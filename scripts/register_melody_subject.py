#!/usr/bin/env python3
"""Register melody-member-ops in RAL identity layer.

依据：170号施工令 Phase 2 前置条件。
"""
import sys
sys.path.insert(0, '/home/agentuser/ral-core')

from ral.locator import db
from ral.identity.api import Identity
from ral.identity import store as identity_store

conn = db.open_index()
identity = Identity(conn, actor='melody-bootstrap', runtime='melody')

# subject_id format: kind:name
SUBJECT_ID = 'runtime:melody-member-ops'

# Check if already exists
if identity_store.exists(conn, SUBJECT_ID):
    print('ALREADY_EXISTS: ' + SUBJECT_ID + ' already registered')
else:
    subject_id = identity.register_subject(
        kind='runtime',
        name='melody-member-ops',
        display_name='Melody - Momo member operations runtime avatar',
        authorized_by='founder-approval-170'
    )
    print('REGISTERED: subject_id=' + subject_id)

# Verify
exists = identity_store.exists(conn, SUBJECT_ID)
print('VERIFY: exists=' + str(exists))
conn.close()
