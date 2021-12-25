# Generated by Django 4.0 on 2021-12-24 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CredentialsModel',
            fields=[
                ('id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('task', models.CharField(max_length=80, null=True)),
                ('updated_time', models.CharField(max_length=80, null=True)),
            ],
        ),
    ]
