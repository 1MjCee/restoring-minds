# Generated by Django 5.1.5 on 2025-02-23 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crewai_agents', '0023_remove_email_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name': 'Company', 'verbose_name_plural': 'Companies'},
        ),
        migrations.AlterField(
            model_name='email',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('updated', 'Updated'), ('sent', 'Email Sent'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
    ]
