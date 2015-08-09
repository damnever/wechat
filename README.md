## Chat Room (To Be Continued)

Powered by Tornado, MySQL, Redis, Bootstrap, jQuery.

---

### Summary

- **Tornado**: Use long polling, rather than WebSocket.
- **MySQL**: Store user informations，UUIDs that is what email verification and password recovery need.
- **Redis**：Store online users, and through Pub-Sub to push online/offline messages, chat messages.
- **AJAX**: Verify forms, including sign-up, log-in, password recovery, etc.
- **Email Verification**: Sign-up, password recovery.
- **Online/offline**: Use long polling to indicate user if online.
- **New Messages**: If received message from the user is not current chat user, show the number of unread message. Otherwise, show messages in chat box. In addition, pictures is ok!
- **Robot**: Use API http://www.tuling123.com/openapi/cloud/access_api.jsp

![](./example3.png)
![](./example2.png)
![](./example1.png)

---

### Setup

1. Clone the repo. `pip install -r requirements.txt`.

2. Set `from_addr`(email address), `from_pwd`(email passwrod) and `robot_key`(See http://www.tuling123.com/openapi/cloud/access_api.jsp) in `chat_share.conf`.

3. `ln -s chat_share.conf chat.conf` or rename `chat_share.conf` to `chat.conf`.

4. `python app.py` or `chmod +x app.py` then `./app.py`.

5. Enjoy it, and sart the repo!!!

---

### TO-DO
- [x] Robot: http://www.tuling123.com/openapi/cloud/access_api.jsp
- [ ] When sending email, page would blocking, maybe task queue?
- [ ] When user offline, clear up messages?
- [ ] Through other sites of OAuth login?
- [ ] A kinds of BUGs，to be continued O(∩_∩)O~

### LICENSE

[The BSD 3-Clause License](./LICENSE)
