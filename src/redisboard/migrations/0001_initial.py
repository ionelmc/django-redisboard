# -*- coding: utf-8 -*-


import django.core.validators
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RedisServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=50, verbose_name='Label', null=True)),
                (
                    'hostname',
                    models.CharField(
                        verbose_name='Hostname', max_length=250, help_text='This can also be the absolute path to a redis socket'
                    ),
                ),
                (
                    'port',
                    models.IntegerField(
                        default=6379,
                        validators=[django.core.validators.MaxValueValidator(65535), django.core.validators.MinValueValidator(1)],
                        verbose_name='Port',
                        blank=True,
                        null=True,
                    ),
                ),
                ('password', models.CharField(blank=True, max_length=250, verbose_name='Password', null=True)),
                (
                    'sampling_threshold',
                    models.IntegerField(
                        default=1000,
                        verbose_name='Sampling threshold',
                        help_text='Number of keys after which only a sample (of random keys) is shown on the inspect page.',
                    ),
                ),
                (
                    'sampling_size',
                    models.IntegerField(
                        default=200,
                        verbose_name='Sampling size',
                        help_text='Number of random keys shown when sampling is used. Note that each key translates to a RANDOMKEY call'
                        ' in redis.',
                    ),
                ),
            ],
            options={
                'verbose_name_plural': 'Redis Servers',
                'verbose_name': 'Redis Server',
                'permissions': (('can_inspect', 'Can inspect redis servers'),),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='redisserver',
            unique_together=set([('hostname', 'port')]),
        ),
    ]
