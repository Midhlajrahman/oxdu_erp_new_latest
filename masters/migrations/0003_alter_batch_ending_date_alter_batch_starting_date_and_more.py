# Generated by Django 4.2.7 on 2025-05-15 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('masters', '0002_batch_ending_date_batch_starting_date_and_more')]

    operations = [
        migrations.AlterField(model_name='batch', name='ending_date', field=models.DateField(null=True)),
        migrations.AlterField(model_name='batch', name='starting_date', field=models.DateField(null=True)),
        migrations.AlterField(model_name='historicalbatch', name='ending_date', field=models.DateField(null=True)),
        migrations.AlterField(model_name='historicalbatch', name='starting_date', field=models.DateField(null=True)),
    ]
