from setuptools import setup, find_packages

setup(
	name="PythonWalker",  # Replace with your project name
	version="0.3.1",
	packages=find_packages(),  # Automatically finds packages in your project
	install_requires=[
		"requests>=2.32.3",
		"websockets>=13.1",
		"protobuf",
        "binreader",
	],
	author="Tycho10101",
	author_email="supallawma@gmail.com",
	description="A Python based bot library for PixelWalker",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	url="https://github.com/Tycho10101/PythonWalker",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.10",  # Ensure the correct Python version for your project
)
