import os
from setuptools import setup

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

requirements = []
with open(os.path.join(LOCAL_DIR, "requirements.txt"), "r") as f:
    for line in f:
        line = line.rstrip()
        if not line.startswith("#"):
            requirements.append(line)

setup (
	name="simoc_server",
	packages=["simoc_server"],
	include_package_data=True,
	install_requires=requirements
)