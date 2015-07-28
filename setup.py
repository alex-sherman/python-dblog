from setuptools import setup

setup(
  name = "dblog",
  version = "0.3.1",
  description = "A Python logging library that supports databases",
  packages = ["dblog"],
  author='Alex Sherman',
  author_email='asherman1024@gmail.com',
  install_requires=['flask', 'python-jrpc==1.1.5'],
  url='https://github.com/alex-sherman/python-dblog')
