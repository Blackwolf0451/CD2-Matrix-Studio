# Contributing

Thanks for helping improve CD2 Matrix Studio.

## Bug reports

Please include:

- CD2 Matrix Studio version
- Windows version
- dock model/revision if known
- whether Flydigi Space Station was closed
- exact steps to reproduce
- screenshot or error message if available

## Compatibility reports

If testing another Flydigi dock or hardware revision, do not assume the protocol is identical. Please report:

- USB VID/PID
- product string
- whether static frames work
- whether animations work
- whether 10 ms / 40 ms timing behaves correctly

## Protocol research

Useful contributions include minimal USB captures showing one clearly described action.

Please avoid including unrelated USB traffic whenever possible.

Firmware flashing/replacement is outside the intended scope of this project.

## Pull requests

Before submitting:

```text
pytest -q
```

Keep UI strings in both English and Russian dictionaries.

Do not expose protocol implementation details in the normal user interface unless they are genuinely useful to users.
