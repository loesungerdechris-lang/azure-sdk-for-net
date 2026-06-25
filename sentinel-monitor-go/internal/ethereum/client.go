package ethereum

import "fmt"

type Config struct {
	RPCURL            string
	DispatcherAddress string
}

func (c Config) Validate() error {
	if c.RPCURL == "" {
		return fmt.Errorf("rpc url is required")
	}
	if c.DispatcherAddress == "" {
		return fmt.Errorf("dispatcher address is required")
	}
	return nil
}

type Client struct {
	config Config
}

func NewClient(config Config) (*Client, error) {
	if err := config.Validate(); err != nil {
		return nil, err
	}
	return &Client{config: config}, nil
}

func (c *Client) DispatcherAddress() string {
	return c.config.DispatcherAddress
}
