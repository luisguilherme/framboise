from setuptools import setup

setup(name='framboise',
      version='0.1',
      description='Utility to download subtitles from opensubtitles.org',
      url='https://github.com/luisguilherme/framboise',
      author='Luis Guilherme Pereira',
      author_email='dev@luisguilherme.net',
      license='MIT',
      packages=['framboise'],
      zip_safe=True,
      entry_points = {
          'console_scripts': [ 'framboise=framboise.framboise:main' ],
          }
)
