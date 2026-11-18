from django.db import connection


def install_rls(table_names):
    statements = []
    for table in table_names:
        if not table.replace("_", "").isalnum():
            raise ValueError("Nombre de tabla inválido")
        policy = f"{table}_tenant_isolation"
        predicate = (
            "current_setting('jopets.global_access', true) = 'on' OR "
            "(tenant_id::text = current_setting('jopets.tenant_id', true) "
            "AND (parent_tenant_id IS NULL OR "
            "parent_tenant_id::text = current_setting('jopets.parent_tenant_id', true)))"
        )
        statements.extend([
            f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY',
            f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY',
            f'DROP POLICY IF EXISTS "{policy}" ON "{table}"',
            f'CREATE POLICY "{policy}" ON "{table}" USING ({predicate}) WITH CHECK ({predicate})',
        ])
    with connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
