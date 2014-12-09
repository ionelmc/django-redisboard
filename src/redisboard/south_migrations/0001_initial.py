# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RedisServer'
        db.create_table('redisboard_redisserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=6379)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
        ))
        db.send_create_signal('redisboard', ['RedisServer'])


    def backwards(self, orm):
        
        # Deleting model 'RedisServer'
        db.delete_table('redisboard_redisserver')


    models = {
        'redisboard.redisserver': {
            'Meta': {'object_name': 'RedisServer'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '6379'})
        }
    }

    complete_apps = ['redisboard']
