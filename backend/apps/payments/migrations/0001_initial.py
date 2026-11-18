import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('accounts', '0001_initial')]
    operations = [
        migrations.CreateModel(name='Transaccion', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('external_id', models.CharField(blank=True, max_length=180)), ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
            ('currency', models.CharField(max_length=3)), ('status', models.CharField(default='pending', max_length=32)),
            ('gateway', models.CharField(max_length=32)), ('price_snapshot', models.JSONField(blank=True, default=dict)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='PaymentOutbox', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('event_type', models.CharField(max_length=80)), ('aggregate_id', models.UUIDField()),
            ('idempotency_key', models.CharField(max_length=180, unique=True)), ('payload', models.JSONField(blank=True, default=dict)),
            ('status', models.CharField(default='pending', max_length=24)), ('attempts', models.PositiveIntegerField(default=0)),
            ('processed_at', models.DateTimeField(blank=True, null=True)), ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='WebhookEvent', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('provider', models.CharField(max_length=32)), ('event_id', models.CharField(max_length=180, unique=True)),
            ('payload', models.JSONField(blank=True, default=dict)), ('processed_at', models.DateTimeField(blank=True, null=True)),
        ]),
        migrations.CreateModel(name='PaymentOperation', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('idempotency_key', models.CharField(max_length=180, unique=True)), ('kind', models.CharField(max_length=32)),
            ('status', models.CharField(default='pending', max_length=32)), ('payload', models.JSONField(blank=True, default=dict)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='operations', to='payments.transaccion')),
        ]),
        migrations.CreateModel(name='Allocation', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('recipient_role', models.CharField(max_length=32)), ('percentage', models.DecimalField(decimal_places=4, max_digits=7)),
            ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
            ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='allocations', to='payments.transaccion')),
        ]),
    ]
