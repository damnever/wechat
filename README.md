## Chat Room(To Be Continued)

Tornado, MySQL, Redis, Bootstrap, jQuery

---

### Summary

- **Tornado**: Using long polling, rather than WebSocket.
- **AJAX**: Verifying forms, including sign-up, log-in, password recovery, etc.
- **Email Verification**: Sign-up, password recovery.
- **MySQL**: Storing user informations，UUIDs, it is what email verification and password recovery needs.
- **Redis**：Storing online users, and pushing on/offline messages, chat messages through Pub-Sub.

---

### Requirements

```pip install -r requirements.txt```

See: [requirements.txt](./requirements.txt)

---

### TO-DO

- Blocking when send email, maybe task queue?
- Log in through other sites of OAuth?
- A kinds of BUGs，to be continued O(∩_∩)O~

### LICENSE

[The BSD 3-Clause License](./LICENSE)