# Messenger-Application

A Messenger Application to connect and chat over local area network. It includes 2 main components - User Python App and Server Python Script. A user needs to login to connect and chat. All users must be on a Local Area Network.<br>

<h3>Features of Server Python Script</h3>
<ul>
<li>Server script is actually a multithreaded TCP server where each thread controls a single client - its login process, listens to the client messages and sends them to the other clients.</li>
<li>It includes a Python Script to add a new user.</li>
</ul>
<h3>Features of Messenger Python App</h3>
<ul>
<li>Messenger app includes a user-friendly interface.</li>
<li>User can even block/unblock other users.</li>
<li>Messages are stored in Client side.</li>
</ul>

<h3>Technology Stack:</h3> Python, SQL, Tkinter(python GUI module).

<h3>Note: Use python 3</h3>

<h2>Steps to get started</h2>

<h3>Running the application</h3>
<ul>
<li>Run the add_user script to add username and password you want to user.</li>
<li>Put the IP address of your PC in the variable server_IP in both chatserver and chatclient python script.</li>
<li>Run the chatserver script to start the server.</li>
<li>Now run the chatclient script on same/different PC connected through LAN to start chatting.</li>
</ul>

<br><img src="https://raw.githubusercontent.com/addy1995/CHAT-SERVER/master/Screenshots/Chat-server_3.PNG"><br>
<br><img src="https://raw.githubusercontent.com/addy1995/CHAT-SERVER/master/Screenshots/Chat-server_2.PNG"><br>
