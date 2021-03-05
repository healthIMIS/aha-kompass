#Association_Tables
from main import db
displayGroupOverwrites = db.Table('displayGroupOverwrites', db.Column('displayGroup_id', db.Integer, db.ForeignKey('displayGroup.id')), db.Column('overwrite_id', db.Integer, db.ForeignKey('displayGroup.id')))
displayGroupHasDefault= db.Table('displayGroupHasDefault', db.Column('displayGroup_id', db.Integer, db.ForeignKey('displayGroup.id')), db.Column('default_id', db.Integer, db.ForeignKey('displayGroup.id')))
    #Verknüpft eine Gruppe, welche eine Bündelung von Maßnahmen darstellt mit der Gruppe, welche die Maßnahme an sich darstellt.
displayGroupReplicates= db.Table('displayGroupReplicates', db.Column('displayGroup_id', db.Integer, db.ForeignKey('displayGroup.id')), db.Column('replicats_of_id', db.Integer, db.ForeignKey('displayGroup.id')))
    #Verknüpft eine (Default-)Gruppe mit den Gruppen, auß deren Modifizierung diese entstanden ist.
deviceHasDistrict= db.Table('deviceHasDistrict', db.Column('device_id', db.Integer, db.ForeignKey('devices.id')), db.Column('district_id', db.Integer, db.ForeignKey('districts.id')))