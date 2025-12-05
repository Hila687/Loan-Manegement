from django.db import migrations

def create_roles(apps, schema_editor):
    Role = apps.get_model('core', 'Role')

    roles = [
        ("a3c4938e-03db-4364-a931-b8f942158a03", "Admin", "System administrator"),
        ("4a38823a-11b8-419d-a91b-d3b8a162b132", "Trustee", "Community trustee"),
        ("941eae3d-ca30-4d87-9474-5b55d5e8b219", "Borrower", "Loan borrower"),
        ("c38fa941-0ed0-4c26-8770-135b1485f9c5", "Donor", "System donor"),
    ]

    for role_id, name, desc in roles:
        Role.objects.update_or_create(
            role_id=role_id,
            defaults={"name": name, "description": desc}
        )

def delete_roles(apps, schema_editor):
    Role = apps.get_model('core', 'Role')
    Role.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles, delete_roles),
    ]
