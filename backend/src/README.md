# Folder Structure

```bash
src
    ├── README.md
    ├── __init__.py
    ├── conf.py
    ├── core
    │   ├── __init__.py
    │   ├── kernel
    │   │   │           └── ______timeline.py
    │   │   │           └── __init__.py
    │   │   │           └── _ds.py
    │   │   │           └── entity.py
    │   │   │           └── event.py
    │   │   │           └── kernel_utils.py
    │   │   │           └── quantum_kernel.py
    │   │   │           └── quantum_manager.py
    │   │   │           └── quantum_utils.py
    │   │               └── timeline.py
    │   ├── resource_management
    │   │   │           └── __init__.py
    │   │   │           └── memory_manager.py
    │   │   │           └── resource_manager.py
    │   │   │           └── rule_manager.py
    │   │               └── task_manager.py
    │   └── topology
    │       │           └── __init__.py
    │       │           └── message_queue_handler.py
    │       │           └── node.py
    │                   └── topology.py
    ├── directory.txt
    ├── layers
    │   ├── __init__.py
    │   ├── application_layer
    │   │   ├── __init__.py
    │   │   ├── attack
    │   │   │   │       └── __init__.py
    │   │   │           └── attack.py
    │   │   ├── communication
    │   │   │   │       └── __init__.py
    │   │   │   │       └── communication.py
    │   │   │   │       └── network.py
    │   │   │           └── network_call_graph.html
    │   │   ├── error_analyzer
    │   │   │   │       └── __init__.py
    │   │   │           └── error_analyzer.py
    │   │   ├── noise
    │   │   │   │       └── Error.py
    │   │   │   │       └── __init__.py
    │   │   │   │       └── noise.py
    │   │   │           └── noise_model.py
    │   │   ├── protocol.py
    │   │   ├── quantum_network.py
    │   │   ├── relay_manager.py
    │   │   ├── template.py
    │   │   └── utils
    │   │       │       └── __init__.py
    │   │       │       └── circuits.py
    │   │       │       └── security_checks.py
    │   │               └── utils.py
    │   ├── link_layer
    │   │   ├── __init__.py
    │   │   └── entanglement_management
    │   │       │       └── DLCZ_generation.py
    │   │       │       └── DLCZ_purification.py
    │   │       │       └── DLCZ_swapping.py
    │   │       │       └── TandDRequisites.txt
    │   │       │       └── __init__.py
    │   │       │       └── bk_generation.py
    │   │       │       └── bk_purification.py
    │   │       │       └── bk_swapping.py
    │   │               └── entanglement_protocol.py
    │   ├── network_layer
    │   │   ├── __init__.py
    │   │   └── network_management
    │   │       │       └── __init__.py
    │   │       │       └── network_manager.py
    │   │       │       └── request.py
    │   │       │       └── reservation.py
    │   │               └── routing.py
    │   ├── physical_layer
    │   │   ├── __init__.py
    │   │   └── components
    │   │       │       └── DLCZ_bsm.py
    │   │       │       └── DLCZ_memory.py
    │   │       │       └── __init__.py
    │   │       │       └── beam_splitter.py
    │   │       │       └── bk_bsm.py
    │   │       │       └── bk_memory.py
    │   │       │       └── circuit.py
    │   │       │       └── detector.py
    │   │       │       └── interferometer.py
    │   │       │       └── light_source.py
    │   │       │       └── optical_channel.py
    │   │       │       └── photon.py
    │   │       │       └── polarization_measurement.py
    │   │       │       └── spdc_lens.py
    │   │       │       └── switch.py
    │   │               └── waveplates.py
    │   └── transport_layer
    │       ├── __init__.py
    │       └── transport_manager.py
    ├── loggers.py
    ├── logging.ini
    └── utils
        ├── __init__.py
        ├── encoding.py
        ├── log.py
        ├── message.py
        ├── protocol.py
        └── quantum_state.py
```