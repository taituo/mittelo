package mittelo

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"time"
)

type Client struct {
	conn net.Conn
	r    *bufio.Reader
	w    *bufio.Writer
}

func Dial(host string, port int, timeout time.Duration) (*Client, error) {
	conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", host, port), timeout)
	if err != nil {
		return nil, err
	}
	return &Client{
		conn: conn,
		r:    bufio.NewReader(conn),
		w:    bufio.NewWriter(conn),
	}, nil
}

func (c *Client) Close() error {
	if c.conn == nil {
		return nil
	}
	return c.conn.Close()
}

type rpcResp struct {
	ID     string                 `json:"id"`
	Result map[string]any         `json:"result"`
	Error  map[string]any         `json:"error"`
	Raw    map[string]any         `json:"-"`
}

func (c *Client) Call(method string, params map[string]any) (map[string]any, error) {
	reqID := fmt.Sprintf("%d", time.Now().UnixNano())
	req := map[string]any{
		"id":     reqID,
		"method": method,
		"params": params,
	}
	b, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}
	if _, err := c.w.Write(append(b, '\n')); err != nil {
		return nil, err
	}
	if err := c.w.Flush(); err != nil {
		return nil, err
	}

	line, err := c.r.ReadBytes('\n')
	if err != nil {
		return nil, err
	}

	var raw map[string]any
	if err := json.Unmarshal(line, &raw); err != nil {
		return nil, err
	}

	gotID, _ := raw["id"].(string)
	if gotID != reqID {
		return nil, errors.New("mismatched response id")
	}
	if raw["error"] != nil {
		if e, ok := raw["error"].(map[string]any); ok {
			if msg, ok := e["message"].(string); ok && msg != "" {
				return nil, errors.New(msg)
			}
		}
		return nil, errors.New("rpc error")
	}
	if raw["result"] == nil {
		return map[string]any{}, nil
	}
	res, ok := raw["result"].(map[string]any)
	if !ok {
		return nil, errors.New("invalid result")
	}
	return res, nil
}

