from src.data_manager import DataManager
import src.core.integration_layer as ce

print('--- CARGA Y NORMALIZACION DE KPIS ---')
dm = DataManager()
dm.load_kpis_data('DatabankExport_M1.csv')
df = dm.kpis_data
if df is None:
    print('ERROR: dm.kpis_data es None. No se cargaron los KPIs.')
    exit(1)
print('\nTIPOS TRAS DATAMANAGER:')
print(df.dtypes)

print('\n--- VALIDACION EN CORE ENGINE ---')
engine = ce.FactorKElite96Enhanced()
df2 = df.copy()
try:
    engine._validate_input_data(df2)
    print('Validación en core engine: OK')
except Exception as e:
    print('VALIDACION CORE ENGINE: ERROR:', e)
print('\nTIPOS ANTES DE VALIDACION EN CORE ENGINE:')
print(df2.dtypes) 