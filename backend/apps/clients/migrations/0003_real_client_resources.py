from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [('clients', '0002_booking_arrived_at_booking_gps_lat_booking_gps_lng_and_more')]
    operations = [
        migrations.AlterField(model_name='booking', name='provider_id', field=models.CharField(blank=True, max_length=64, null=True)),
        migrations.CreateModel(name='Vaccine', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('name', models.CharField(max_length=160)), ('administered_at', models.DateField()),
            ('expires_at', models.DateField(blank=True, null=True)), ('veterinarian', models.CharField(blank=True, max_length=160)),
            ('notes', models.TextField(blank=True)), ('created_at', models.DateTimeField(auto_now_add=True)),
            ('pet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vaccines', to='clients.pet')),
        ]),
        migrations.CreateModel(name='MedicalRecord', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('event_type', models.CharField(max_length=64)), ('title', models.CharField(max_length=160)),
            ('occurred_at', models.DateTimeField()), ('details', models.JSONField(blank=True, default=dict)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('pet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to='clients.pet')),
        ]),
        migrations.CreateModel(name='Notification', fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('tenant_id', models.UUIDField()), ('parent_tenant_id', models.UUIDField(blank=True, null=True)),
            ('title', models.CharField(max_length=180)), ('message', models.TextField(blank=True)),
            ('kind', models.CharField(default='general', max_length=48)), ('is_read', models.BooleanField(default=False)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='accounts.user')),
        ]),
    ]
