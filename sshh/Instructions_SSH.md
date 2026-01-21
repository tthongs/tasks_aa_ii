To SSH into this computer from another laptop, you will need to use the following command on your other laptop:

```bash
ssh tthongs@192.168.1.15
```

Here's a breakdown:
*   `ssh`: The command to initiate an SSH connection.
*   `tthongs`: Your username on this computer.
*   `192.168.1.15`: The IP address of this computer on your local network.

**Important Considerations:**

1.  **Dynamic IP Address:** Your computer's IP address (`192.168.1.15`) might change over time, especially if your router assigns IP addresses dynamically. If you can't connect later, you may need to find the current IP address again using `ip addr`.
2.  **Firewall:** Ensure that your firewall on this computer is not blocking incoming connections on port 22 (the default SSH port). If you have a firewall enabled and are having trouble connecting, you might need to open this port.
3.  **Network Accessibility:** Both laptops must be on the same network, or this computer must be accessible from the internet (which usually involves router configuration like port forwarding and is more complex).
4.  **SSH Key vs. Password:** By default, it will likely prompt you for your password. For more secure and convenient access, you can set up SSH key-based authentication.

If you encounter any issues or need help with firewall configuration or setting up SSH keys, let me know!