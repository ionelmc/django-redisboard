# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'RedisServer.port'
        db.alter_column('redisboard_redisserver', 'port', self.gf('django.db.models.fields.IntegerField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'RedisServer.port'
        db.alter_column('redisboard_redisserver', 'port', self.gf('django.db.models.fields.IntegerField')())


    models = {
        'redisboard.redisserver': {
            'Meta': {'unique_together': "(('hostname', 'port'),)", 'object_name': 'RedisServer'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '6379', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['redisboard']
