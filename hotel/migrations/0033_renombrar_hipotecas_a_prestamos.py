from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "hotel",
            "0032_alter_hipoteca_options_hipoteca_dia_cobro_and_more",
        ),
    ]

    operations = [

        # Hipoteca -> Prestamo
        migrations.RenameModel(
            old_name="Hipoteca",
            new_name="Prestamo",
        ),

        # PagoHipoteca -> PagoPrestamo
        migrations.RenameModel(
            old_name="PagoHipoteca",
            new_name="PagoPrestamo",
        ),

        # IMPORTANTE:
        # quitamos primero la constraint antigua,
        # porque todavía hace referencia a "hipoteca"
        migrations.RemoveConstraint(
            model_name="pagoprestamo",
            name="pago_hipoteca_unico_por_fecha",
        ),

        # Ahora sí podemos cambiar
        # hipoteca -> prestamo
        migrations.RenameField(
            model_name="pagoprestamo",
            old_name="hipoteca",
            new_name="prestamo",
        ),
    ]