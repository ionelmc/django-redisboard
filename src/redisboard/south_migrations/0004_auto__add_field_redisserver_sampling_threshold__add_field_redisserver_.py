# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'RedisServer.sampling_threshold'
        db.add_column('redisboard_redisserver', 'sampling_threshold', self.gf('django.db.models.fields.IntegerField')(default=1000), keep_default=False)

        # Adding field 'RedisServer.sampling_size'
        db.add_column('redisboard_redisserver', 'sampling_size', self.gf('django.db.models.fields.IntegerField')(default=200), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'RedisServer.sampling_threshold'
        db.delete_column('redisboard_redisserver', 'sampling_threshold')

        # Deleting field 'RedisServer.sampling_size'
        db.delete_column('redisboard_redisserver', 'sampling_size')


    models = {
        'redisboard.redisserver': {
            'Meta': {'unique_together': "(('hostname', 'port'),)", 'object_name': 'RedisServer'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '6379', 'null': 'True', 'blank': 'True'}),
            'sampling_size': ('django.db.models.fields.IntegerField', [], {'default': '200'}),
            'sampling_threshold': ('django.db.models.fields.IntegerField', [], {'default': '1000'})
        }
    }

    complete_apps = ['redisboard']
