from setuptools import setup


setup (
	name="simoc_server",
	packages=["simoc_server"],
	include_package_data=True,
	install_requires=[
		"flask",
		"flask_sqlalchemy",
		"mesa",
		"flask-login",
	],
)