# Generated by Django 5.1.3 on 2025-01-11 01:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0013_evento_preco_usuario_imagem_usuario_username_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListaDesejos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agenda.evento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agenda.usuario')),
            ],
        ),
    ]
