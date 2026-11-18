import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('accounts', '0001_initial')]
    operations = [
        migrations.CreateModel(name='ClientProfile', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('city', models.CharField(max_length=120)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='client_profile', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Pet', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('name', models.CharField(max_length=120)), ('species', models.CharField(max_length=80)),
            ('breed', models.CharField(blank=True, max_length=120)), ('backup_code_hash', models.CharField(max_length=128)),
            ('health_data', models.JSONField(blank=True, default=dict)),
            ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pets', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Booking', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('state', models.CharField(choices=[('searched', 'Buscando'), ('paid', 'Pagada'), ('assigned', 'Buscando'), ('en_route', 'En camino'), ('arrived', 'En camino'), ('verified', 'En camino'), ('in_service', 'En servicio'), ('completed', 'Completado'), ('cancelled', 'Cancelada')], default='searched', max_length=24)),
            ('price_snapshot', models.JSONField(blank=True, default=dict)),
            ('pet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='clients.pet')),
        ]),
        migrations.CreateModel(name='VerificationChallenge', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('booking_id', models.UUIDField()), ('token_hash', models.CharField(max_length=128)),
            ('expires_at', models.DateTimeField()), ('used_at', models.DateTimeField(blank=True, null=True)),
            ('gps_risk', models.BooleanField(default=False)),
        ]),
    ]
