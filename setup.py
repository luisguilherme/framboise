from setuptools import setup

setup(name='framboise',
      version='0.1+20130915.1944-0300',
      description='Utility to download subtitles from opensubtitles.org',
      url='https://github.com/luisguilherme/framboise',
      author='Luis Guilherme Pereira',
      author_email='dev@luisguilherme.net',
      license='MIT',
      packages=['framboise'],
      zip_safe=False,
      entry_points = {
          'console_scripts': [ 'framboise=framboise.framboise:main' ],
          }
)
