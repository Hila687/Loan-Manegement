from django.db import migrations

def create_roles(apps, schema_editor):
    Role = apps.get_model("core", "Role")

    roles = [
        ("Admin", "System administrator"),
        ("Trustee", "Community trustee"),
        ("Borrower", "Loan borrower"),
        ("Donor", "System donor"),
    ]

    for name, desc in roles:
        Role.objects.get_or_create(name=name, defaults={"description": desc})

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),  # ← עדכני למיגרציה האחרונה שלך!
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
