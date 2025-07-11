# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['src/gui_enhanced_rank.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('config/trading_config.json', 'config'),
        ('formulas_repository.json', '.'),
        ('INPUTTEST', 'INPUTTEST'),  # Incluir carpeta de test
        *collect_data_files('scipy'),
        *collect_data_files('sklearn'),
        *collect_data_files('matplotlib'),
        *collect_data_files('seaborn'),
    ],
    hiddenimports=[
        # Core libraries
        'pandas',
        'numpy',
        'openpyxl',
        'xlrd',
        'xlwt',
        
        # Scientific computing
        'scipy',
        'scipy.stats',
        'scipy.cluster',
        'scipy.cluster.hierarchy',
        'scipy._cython_utility',
        'scipy._cyutility',
        'scipy.sparse._csparsetools',
        'scipy.sparse._sparsetools',
        'scipy.sparse._coo',
        'scipy.sparse._csc',
        'scipy.sparse._csr',
        'scipy.sparse._dia',
        'scipy.sparse._lil',
        'scipy.sparse._dok',
        'scipy.sparse._base',
        'scipy.sparse._matrix_io',
        'scipy.sparse._index',
        'scipy.sparse._compressed',
        'scipy.sparse._construct',
        'scipy.sparse._extract',
        'scipy.sparse._matrix',
        'scipy.sparse._data',
        'scipy.special',
        'scipy.linalg',
        'scipy.optimize',
        
        # Machine learning
        'sklearn',
        'sklearn.cluster',
        'sklearn.preprocessing',
        'sklearn.decomposition',
        'sklearn.utils._openmp_helpers',
        'sklearn.utils._typedefs',
        'sklearn.utils._weight_vector',
        'sklearn.utils._fast_dict',
        'sklearn.utils._random',
        'sklearn.utils._logistic_sigmoid',
        'sklearn.utils._vector_sentinel',
        'sklearn.utils._bunch',
        'sklearn.metrics',
        'sklearn.ensemble',
        
        # Visualization
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends',
        'matplotlib.backends.backend_tkagg',
        'seaborn',
        
        # GUI
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.colorchooser',
        
        # System and utilities
        'threading',
        'logging',
        'pathlib',
        'sys',
        'os',
        'time',
        'traceback',
        're',
        'shutil',
        'difflib',
        'datetime',
        'psutil',
        'json',
        'math',
        'copy',
        'functools',
        'itertools',
        'collections',
        'warnings',
        
        # Additional modules that might be needed
        'numpy.core._methods',
        'numpy.lib.format',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.skiplist',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook-fix-numpy.py'],
    excludes=[
        'matplotlib.tests',
        'numpy.tests',
        'pandas.tests',
        'scipy.tests',
        'sklearn.tests',
        'tkinter.test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KVAVSKFORCERATIO_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Cambiar a True si quieres ver errores en consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
) 