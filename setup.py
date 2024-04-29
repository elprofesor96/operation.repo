from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="operation.repo",
    version="2.0.0",
    description="operation.repo",
    author="elprofesor96",
    py_modules=["op", "ConfigHandler", "OpClass", "OpClassToServer"],
    entry_points={
        "console_scripts": [
            "op = op:main",
        ],
    },
    #package_data={"": ["op.conf"]},
    install_requires=requirements,
)
