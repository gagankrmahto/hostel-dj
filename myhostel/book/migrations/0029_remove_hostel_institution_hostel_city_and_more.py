# Generated by Django 4.2.5 on 2023-10-01 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0028_auto_20190321_1842'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hostel',
            name='institution',
        ),
        migrations.AddField(
            model_name='hostel',
            name='city',
            field=models.CharField(default='Ranchi', help_text='City where hostel is located', max_length=400),
        ),
        migrations.AlterField(
            model_name='booking',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='hostelimage',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='room',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='roomimage',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
