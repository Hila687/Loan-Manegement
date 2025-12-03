from django.db import migrations

def create_roles(apps, schema_editor):
    Role = apps.get_model('core', 'Role')

    roles = [
        ("Admin", "System administrator"),
        ("Trustee", "Community trustee"),
        ("Borrower", "Loan borrower"),
        ("Donor", "System donor"),
    ]

    for name, desc in roles:
        Role.objects.update_or_create(
            name=name,
            defaults={"description": desc}
        )

def delete_roles(apps, schema_editor):
    Role = apps.get_model('core', 'Role')
    Role.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '000X_create_roles'),
    ]

    operations = [
        migrations.RunPython(create_roles, delete_roles),
    ]
