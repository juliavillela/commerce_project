# Generated by Django 3.1.1 on 2020-09-29 17:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_comment_watch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='watch',
            name='listing',
            field=models.ManyToManyField(related_name='watched', to='auctions.Listing'),
        ),
    ]
