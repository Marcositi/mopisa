import unicodedata
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DecimalWidget, IntegerWidget
from .models import Producto, Categoria, Marca, Proveedor

def normalizar_texto(texto):
    if not texto or str(texto).strip().lower() == 'none':
        return ""
    texto_normalizado = unicodedata.normalize('NFD', str(texto))
    texto_sin_acentos = "".join([c for c in texto_normalizado if unicodedata.category(c) != 'Mn'])
    return texto_sin_acentos.strip().lower()

class SmartFKWidget(ForeignKeyWidget):
    """Widget para Categoria, Marca y Proveedor que busca ignorando acentos o crea si no existe."""
    def clean(self, value, row=None, **kwargs):
        if value and str(value).strip().lower() not in ['none', 'nan', '']:
            nombre_excel = str(value).strip()
            nombre_busqueda = normalizar_texto(nombre_excel)
            
            # Buscar en la base de datos comparando versiones normalizadas
            qs = self.model.objects.all()
            for obj in qs:
                if normalizar_texto(getattr(obj, self.field)) == nombre_busqueda:
                    return obj
            
            # Si no se encuentra, crear uno nuevo
            return self.model.objects.create(**{self.field: nombre_excel})
        return None

class DineroWidget(DecimalWidget):
    def clean(self, value, row=None, **kwargs):
        if value is None or str(value).strip() in ["", "None", "nan"]:
            return 0.0
        clean_value = str(value).replace('$', '').replace(',', '').strip()
        try:
            return super().clean(clean_value, row, **kwargs)
        except: return 0.0

class ExistenciaWidget(IntegerWidget):
    def clean(self, value, row=None, **kwargs):
        if value is None or str(value).strip() in ["", "None", "nan"]:
            return 0
        try:
            clean_value = str(value).split('.')[0].strip()
            return super().clean(clean_value, row, **kwargs)
        except: return 0

class ProductoResource(resources.ModelResource):
    # Campos básicos y numéricos
    nombre = fields.Field(column_name='descripcion_1', attribute='nombre')
    clave = fields.Field(column_name='clave', attribute='clave')
    departamento = fields.Field(column_name='departamento', attribute='departamento')
    precio = fields.Field(column_name='precio', attribute='precio', widget=DineroWidget())
    existencia = fields.Field(column_name='existencia', attribute='existencia', widget=ExistenciaWidget())
    
    # Relaciones Foreign Key usando el Smart Widget
    categoria = fields.Field(
        column_name='categoria', 
        attribute='categoria',
        widget=SmartFKWidget(Categoria, 'nombre')
    )
    
    marca = fields.Field(
        column_name='marca',
        attribute='marca',
        widget=SmartFKWidget(Marca, 'nombre')
    )
    
    proveedor = fields.Field(
        column_name='proveedor',
        attribute='proveedor',
        widget=SmartFKWidget(Proveedor, 'nombre')
    )

    class Meta:
        model = Producto
        import_id_fields = [] # Dinámico vía get_import_id_fields
        fields = ('nombre', 'clave', 'categoria', 'marca', 'proveedor', 'precio', 'existencia', 'departamento')
        skip_unchanged = True
        report_skipped = True

    def get_import_id_fields(self):
        return ['clave']

    def before_import(self, dataset, **kwargs):
        """Pre-procesamiento de cabeceras de Excel."""
        headers = [str(h).lower().strip() if h else "" for h in dataset.headers]
        new_headers = []
        desc_count = 0
        
        for h in headers:
            if 'descrip' in h:
                desc_count += 1
                new_headers.append(f"descripcion_{desc_count}")
            elif 'clav' in h:
                new_headers.append("clave")
            elif 'prov' in h:
                new_headers.append("proveedor")
            elif 'marc' in h:
                new_headers.append("marca")
            elif 'depa' in h:
                new_headers.append("departamento")
            else:
                new_headers.append(h)
        
        dataset.headers = new_headers

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Evita la creación de filas vacías (los famosos cuadros verdes sin texto)."""
        clave = row.get('clave')
        nombre = row.get('descripcion_1')
        
        if not clave or not nombre or str(nombre).strip() == "":
            return True
            
        return super().skip_row(instance, original, row, import_validation_errors)