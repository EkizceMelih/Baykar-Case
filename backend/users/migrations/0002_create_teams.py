from django.db import migrations

def create_teams(apps, schema_editor):
    Team = apps.get_model('users', 'Team')
    names = [
        "Kanat Takımı",
        "Gövde Takımı",
        "Kuyruk Takımı",
        "Aviyonik Takımı",
        "Montaj Takımı",
    ]
    for name in names:
        Team.objects.get_or_create(name=name)

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_teams),
    ]
