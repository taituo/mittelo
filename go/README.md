# Go port (minimal)

This is a tiny, protocol-level client/CLI example in Go.

Build:

```bash
cd go
go build ./cmd/mitteloctl
```

Run:

```bash
./mitteloctl enqueue --host 127.0.0.1 --port 8765 --prompt "hello from go"
./mitteloctl status --host 127.0.0.1 --port 8765
```
