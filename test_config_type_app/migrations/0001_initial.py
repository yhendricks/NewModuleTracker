from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestConfigType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Test Config Type',
                'verbose_name_plural': 'Test Config Types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CurrentMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=100)),
                ('min_value', models.FloatField()),
                ('max_value', models.FloatField()),
                ('unit', models.CharField(default='A', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('test_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_measurements', to='test_config_type_app.testconfigtype')),
            ],
            options={
                'verbose_name': 'Current Measurement',
                'verbose_name_plural': 'Current Measurements',
            },
        ),
        migrations.CreateModel(
            name='FrequencyMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=100)),
                ('min_value', models.FloatField()),
                ('max_value', models.FloatField()),
                ('unit', models.CharField(default='Hz', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('test_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frequency_measurements', to='test_config_type_app.testconfigtype')),
            ],
            options={
                'verbose_name': 'Frequency Measurement',
                'verbose_name_plural': 'Frequency Measurements',
            },
        ),
        migrations.CreateModel(
            name='ResistanceMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=100)),
                ('min_value', models.FloatField()),
                ('max_value', models.FloatField()),
                ('unit', models.CharField(default='Ω', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('test_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resistance_measurements', to='test_config_type_app.testconfigtype')),
            ],
            options={
                'verbose_name': 'Resistance Measurement',
                'verbose_name_plural': 'Resistance Measurements',
            },
        ),
        migrations.CreateModel(
            name='VoltageMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=100)),
                ('min_value', models.FloatField()),
                ('max_value', models.FloatField()),
                ('unit', models.CharField(default='V', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('test_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voltage_measurements', to='test_config_type_app.testconfigtype')),
            ],
            options={
                'verbose_name': 'Voltage Measurement',
                'verbose_name_plural': 'Voltage Measurements',
            },
        ),
        migrations.CreateModel(
            name='YesNoQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=200)),
                ('required_answer', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('test_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yes_no_questions', to='test_config_type_app.testconfigtype')),
            ],
            options={
                'verbose_name': 'Yes/No Question',
                'verbose_name_plural': 'Yes/No Questions',
            },
        ),
    ]