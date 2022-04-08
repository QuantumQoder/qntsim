from setuptools import setup

setup(
    name="qntsim",
    version="0.1.1",
    author="Qulabs Software India Pvt Ltd",
    description="Quantum Network Simulator for quick prototyping and developement of protocols and applications",
    # packages = find_packages('src'),
    packages=['qntsim', 'qntsim.app', 'qntsim.kernel', 'qntsim.components',
              'qntsim.network_management', 'qntsim.entanglement_management', 'qntsim.qkd',
              'qntsim.resource_management','qntsim.transport_layer' , 'qntsim.topology', 'qntsim.utils'],
    package_dir={'qntsim': 'src'},
    install_requires=[
        'numpy',
	'matplotlib',
        'json5',
        'pandas',
        'qutip'
    ],
)
