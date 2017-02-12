# CHAT-SERVER

A GUI based python app which includes client desktop app and server script. A user needs to login to connect and chat. All users must be on a Local Area Network. Server script is actually a multithreaded TCP server where each thread controls a single client - its login process, listens to the client messages and sends them to the other clients. Client app includes a user-friendly interface. Clients can even block/unblock other users. Old messages are saved in a database on the client side. Technology Stack: Python, SQL, Tkinter(python GUI module).

<h3>Note: Use python 3</h3>

<h2>How to Use</h2>

<h3>Running the application</h3>
<ul>
<li>Run the add_user script to add username and password you want to user.</li>
<li>Put the IP address of your PC in the variable server_IP in both chatserver and chatclient python script.</li>
<li>Run the chatserver script to start the server.</li>
<li>Now run the chatclient script on same/different PC connected through LAN to start chatting.</li>
</ul>

<br><img src="https://raw.githubusercontent.com/addy1995/CHAT-SERVER/master/Screenshots/Chat-server_3.PNG"><br>
<br><img src="https://raw.githubusercontent.com/addy1995/CHAT-SERVER/master/Screenshots/Chat-server_2.PNG"><br>
