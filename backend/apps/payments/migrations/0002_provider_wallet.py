from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [('payments', '0001_initial'), ('accounts', '0001_initial')]
    operations = [
        migrations.CreateModel(name='ProviderWallet', fields=[
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('provider_id', models.CharField(max_length=64, unique=True)), ('currency', models.CharField(default='USD', max_length=3)),
            ('available_balance', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
            ('pending_balance', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
            ('updated_at', models.DateTimeField(auto_now=True)),
        ]),
        migrations.CreateModel(name='WalletTransaction', fields=[
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('external_id', models.CharField(blank=True, max_length=180)), ('description', models.CharField(max_length=180)),
            ('amount', models.DecimalField(decimal_places=2, max_digits=14)), ('status', models.CharField(default='pending', max_length=32)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='payments.providerwallet')),
        ]),
    ]
