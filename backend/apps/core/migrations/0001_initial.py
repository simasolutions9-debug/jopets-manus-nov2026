import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(
        name='AuditEvent',
        fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('actor_id', models.UUIDField(blank=True, null=True)),
            ('tenant_id', models.UUIDField(blank=True, null=True)),
            ('action', models.CharField(max_length=120)),
            ('resource_type', models.CharField(max_length=80)),
            ('resource_id', models.CharField(blank=True, max_length=180)),
            ('outcome', models.CharField(default='success', max_length=24)),
            ('metadata', models.JSONField(default=dict)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ],
    )]
