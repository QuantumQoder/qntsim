# Photon - based
## Quantum Secure Direct Communication
### From front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": "hello world",
        "send": True
        },
    "medium": "photon",
    "size": 88
    }
```
### To front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": bin("hello world"),
        "send": True
        },
    "output_message": {"n2": "hello world"}
    }
```

## Quantum Dialogue
### From front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": "hello",
        "send": True
        },
    "n2": {
        "receiver": "n1",
        "message": "world",
        "send": False
        },
    "medium": "photon",
    "size": 40
    }
```
### To front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": bin("hello"),
        "send": True
        },
    "n2": {
        "receiver": "n1",
        "message": bin("world"),
        "send": False
        },
    "output_message": {"n2": "hello",
                       "n1": "world"}
    }
```

## n - party (not implemented)
### From front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": "hello",
        "send": True
        },
    "n2": {
        "receiver": "n3",
        "message": "world",
        "send": True
        },
    "n3": {"send": False},
    "medium": "photon",
    "size": 40
    }
```
### To front-end (to be decided)
```
{
    "n1": {
        "receiver": "n2",
        "message": bin("hello"),
        "send": True
        },
    "n2": {
        "receiver": "n3",
        "message": bin("world"),
        "send": True
        },
    "n3": {"send": False},
    "output_message": {}
    }
```

# Entanglement - based
## Quantum Secure Direct Communication
### From front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": "hello world"
        },
    "medium": "entanglement",
    "size": 88
    }
```
### To front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": bin("hello world")
        },
    "output_message": {"n2": "hello world"}
    }
```

## Quantum Dialogue
### From front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": "hello"
        },
    "n2": {
        "receiver": "n1",
        "message": "world"
        },
    "encode": "dense",
    "medium": "entanglement",
    "size": 88
    }
```
### To front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": bin("hello")
        },
    "n2": {
        "receiver": "n1",
        "message": bin("world")
        },
    "output_message": {"n2": "hello",
                       "n1": "world"}
    }
```

## Quantum Secret Sharing
### From front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": "hello world"
        },
    "controller": "n3",
    "medium": "entanglement",
    "size": 88,
    "state": "ghz"
    }
```
### To front-end
```
{
    "n1": {
        "receiver": "n2",
        "message": bin("hello world")
        },
    "controller": "n3",
    "state": "ghz",
    "output_message": {"n2": "hello world"}
    }
```