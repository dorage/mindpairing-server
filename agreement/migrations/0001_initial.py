# Generated by Django 4.2.3 on 2023-07-23 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Terms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('mandatory', models.BooleanField()),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Terms',
                'db_table': 'terms',
            },
        ),
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreement', models.BooleanField(default=False)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('terms_id', models.ForeignKey(db_column='term_id', on_delete=django.db.models.deletion.CASCADE, related_name='agreement_set', to='agreement.terms')),
            ],
            options={
                'verbose_name': 'Terms Agreement',
                'db_table': 'terms_agreement',
            },
        ),
    ]
