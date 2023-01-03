from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in admin_iiti/__init__.py
from admin_iiti import __version__ as version

setup(
	name="admin_iiti",
	version=version,
	description="Administration IITI Indore",
	author="CITC IIT Indore",
	author_email="computer.center@iiti.ac.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
