# Generated by Django 5.1.3 on 2025-01-05 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0008_evento_preco'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='imagem',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios/'),
        ),
    ]