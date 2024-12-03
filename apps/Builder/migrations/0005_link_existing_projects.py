from django.db import migrations

def link_projects(apps, schema_editor):
    Project = apps.get_model('Builder', 'Project')
    UserProject = apps.get_model('ProjectManager', 'UserProject')
    
    for project in Project.objects.all():
        # Try to find a matching UserProject
        try:
            user_project = UserProject.objects.get(
                user=project.user,
                name=project.name
            )
            project.user_project = user_project
            project.save()
        except UserProject.DoesNotExist:
            print(f"No matching UserProject found for Project: {project.name}")
            continue

def reverse_link_projects(apps, schema_editor):
    Project = apps.get_model('Builder', 'Project')
    for project in Project.objects.all():
        project.user_project = None
        project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Builder', '0004_project_user_project'),
        ('ProjectManager', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(link_projects, reverse_link_projects),
    ] 