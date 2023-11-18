# Generated by Django 4.2.6 on 2023-10-30 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MovieRestApp', '0003_alter_rating_star'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movie', to='MovieRestApp.movie', verbose_name='Фильм'),
        ),
    ]