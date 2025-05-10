from django.db import migrations, models

def add_cloud_member_field(apps, schema_editor):
    # 获取数据库连接
    connection = schema_editor.connection
    
    # 检查字段是否已存在
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_NAME = 'auth_user'
                AND COLUMN_NAME = 'is_cloud_member';
            """)
            if cursor.fetchone()[0] == 0:
                # 字段不存在，添加字段
                cursor.execute("""
                    ALTER TABLE auth_user
                    ADD COLUMN is_cloud_member BOOLEAN DEFAULT FALSE;
                """)
        except Exception as e:
            print(f"Error adding is_cloud_member field: {e}")

def remove_cloud_member_field(apps, schema_editor):
    # 获取数据库连接
    connection = schema_editor.connection
    
    # 尝试删除字段
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                ALTER TABLE auth_user
                DROP COLUMN is_cloud_member;
            """)
        except Exception as e:
            print(f"Error removing is_cloud_member field: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('masks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_cloud_member_field, remove_cloud_member_field),
    ] 