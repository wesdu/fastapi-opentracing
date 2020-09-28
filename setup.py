import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="fastapi_opentracing",
  version="0.0.1",
  author="Du Wei",
  author_email="pandorid@gmail.com",
  description="fastapi opentracing middleware works on k8s",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/wesdu/fastapi-opentracing",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.7",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)