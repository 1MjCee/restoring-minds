# Generated by Django 5.1.5 on 2025-02-22 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crewai_agents', '0019_outreach_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EmailTemplate',
            new_name='Email',
        ),
        migrations.RenameField(
            model_name='email',
            old_name='template_type',
            new_name='type',
        ),
    ]
