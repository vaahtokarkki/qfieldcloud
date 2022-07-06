# Generated by Django 3.2.13 on 2022-07-01 19:40

import migrate_sql.operations
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0056_projectpermissionsview"),
    ]

    operations = [
        # we need to manually delete the triggers, since they already exist from 0051, but were never added to `sql_config.py`
        # and this is their first `migrate_sql` migration.
        migrations.RunSQL(
            "DROP TRIGGER IF EXISTS core_delta_geom_update_trigger ON core_delta",
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "DROP TRIGGER IF EXISTS core_delta_geom_insert_trigger ON core_delta",
            migrations.RunSQL.noop,
        ),
        migrate_sql.operations.CreateSQL(
            name="core_delta_geom_trigger_func",
            sql="\n            CREATE OR REPLACE FUNCTION core_delta_geom_trigger_func()\n            RETURNS trigger\n            AS\n            $$\n                DECLARE\n                    srid int;\n                BEGIN\n                    SELECT CASE\n                        WHEN jsonb_extract_path_text(NEW.content, 'localLayerCrs') ~ '^EPSG:\\d{1,10}$'\n                        THEN\n                            REGEXP_REPLACE(jsonb_extract_path_text(NEW.content, 'localLayerCrs'), '\\D*', '', 'g')::int\n                        ELSE\n                            NULL\n                        END INTO srid;\n                    NEW.old_geom := ST_Transform( ST_SetSRID( ST_Force2D( ST_GeomFromText( REPLACE( jsonb_extract_path_text(NEW.content, 'old', 'geometry'), 'nan', '0' ) ) ), srid ), 4326 );\n                    NEW.new_geom := ST_Transform( ST_SetSRID( ST_Force2D( ST_GeomFromText( REPLACE( jsonb_extract_path_text(NEW.content, 'new', 'geometry'), 'nan', '0' ) ) ), srid ), 4326 );\n\n                    IF ST_GeometryType(NEW.old_geom) IN ('ST_CircularString', 'ST_CompoundCurve', 'ST_CurvePolygon', 'ST_MultiCurve', 'ST_MultiSurface')\n                    THEN\n                        NEW.old_geom := ST_CurveToLine(NEW.old_geom);\n                    END IF;\n\n                    IF ST_GeometryType(NEW.new_geom) IN ('ST_CircularString', 'ST_CompoundCurve', 'ST_CurvePolygon', 'ST_MultiCurve', 'ST_MultiSurface')\n                    THEN\n                        NEW.new_geom := ST_CurveToLine(NEW.new_geom);\n                    END IF;\n\n                    RETURN NEW;\n                END;\n            $$\n            LANGUAGE PLPGSQL\n        ",
            reverse_sql="\n            DROP FUNCTION IF EXISTS core_delta_geom_trigger_func()\n        ",
        ),
        migrate_sql.operations.CreateSQL(
            name="core_delta_geom_update_trigger",
            sql="\n            CREATE TRIGGER core_delta_geom_update_trigger BEFORE UPDATE ON core_delta\n            FOR EACH ROW\n            WHEN (OLD.content IS DISTINCT FROM NEW.content)\n            EXECUTE FUNCTION core_delta_geom_trigger_func()\n        ",
            reverse_sql="\n            DROP TRIGGER IF EXISTS core_delta_geom_update_trigger ON core_delta\n        ",
        ),
        migrate_sql.operations.CreateSQL(
            name="core_delta_geom_insert_trigger",
            sql="\n            CREATE TRIGGER core_delta_geom_insert_trigger BEFORE INSERT ON core_delta\n            FOR EACH ROW\n            EXECUTE FUNCTION core_delta_geom_trigger_func()\n        ",
            reverse_sql="\n            DROP TRIGGER IF EXISTS core_delta_geom_insert_trigger ON core_delta\n        ",
        ),
    ]
