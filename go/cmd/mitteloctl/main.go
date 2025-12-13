package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"example.com/mittelo/mittelo"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: mitteloctl <enqueue|status> [args]")
		os.Exit(2)
	}

	switch os.Args[1] {
	case "enqueue":
		fs := flag.NewFlagSet("enqueue", flag.ExitOnError)
		host := fs.String("host", "127.0.0.1", "hub host")
		port := fs.Int("port", 8765, "hub port")
		prompt := fs.String("prompt", "", "prompt to enqueue")
		_ = fs.Parse(os.Args[2:])
		if *prompt == "" {
			fmt.Fprintln(os.Stderr, "missing --prompt")
			os.Exit(2)
		}
		c, err := mittelo.Dial(*host, *port, 5*time.Second)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		defer c.Close()
		res, err := c.Call("enqueue", map[string]any{"prompt": *prompt})
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Println(res["task_id"])

	case "status":
		fs := flag.NewFlagSet("status", flag.ExitOnError)
		host := fs.String("host", "127.0.0.1", "hub host")
		port := fs.Int("port", 8765, "hub port")
		limit := fs.Int("limit", 50, "max tasks")
		_ = fs.Parse(os.Args[2:])
		c, err := mittelo.Dial(*host, *port, 5*time.Second)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		defer c.Close()
		res, err := c.Call("list", map[string]any{"limit": *limit})
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		out, _ := json.MarshalIndent(res, "", "  ")
		fmt.Println(string(out))

	default:
		fmt.Fprintln(os.Stderr, "unknown command:", os.Args[1])
		os.Exit(2)
	}
}
