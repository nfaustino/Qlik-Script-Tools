try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Tools for making Qlikview load scripts.',
    'author': 'BenSimonds',
    'url': 'https://github.com/BenSimonds/Qlik-Script-Tools',
    'download_url': 'https://github.com/BenSimonds/Qlik-Script-Tools/archive/master.zip',
    'author_email': 'BSSimonds@gmail.com',
    'version': '0.1dev',
    'install_requires': ['nose'],
    'packages': ['qvtools'],
    'scripts': [],
    'name': 'QVScriptTools'
}

setup(**config)