# Generated by Django 5.1.5 on 2025-01-28 02:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crewai_agents', '0014_delete_successmetric_alter_competitortrend_notes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outreach',
            name='company',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='outreach_company', to='crewai_agents.company'),
        ),
    ]
