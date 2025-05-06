let inputMessage = $('#chat-input-id')
let USER_ID = $('#logged_in_user')
let send_message_form = $('#send_message_form')
let loc = window.location

let otherUserId = null;
let activeThread = null;
//console.log('location protocaol: ', location.protocol)
//console.log('location protocaol2: ', loc.protocol)
let wsStart;
if (location.protocol === 'https:') {
    wsStart = 'wss://';
} else {
    wsStart = 'ws://'; 
}

let endPoint = wsStart + loc.host + loc.pathname

var socket = new WebSocket(endPoint)


function setOtherUserId(userId) {
    otherUserId = userId;
    //console.log('Other User ID set to:', otherUserId); 
}

function setactiveThread(threadId) {
    activeThread = threadId;
    //console.log('thread id:', activeThread); 
}


function openChat(name) {
    document.querySelector('.chat-profiles-container').style.display = window.innerWidth > 768 ? 'flex' : 'none';
    document.getElementById('chat-container').style.display = 'flex';
    document.getElementById('chat-with').textContent = name;
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = ''; // Clear previous messages
    
    // Scroll to the bottom of the chat messages to show the latest messages
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
    }, 0);

    chats[name].forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', message.type);
        messageElement.innerHTML = message.text + `<span class="time">${message.time}</span>`;
        chatMessages.appendChild(messageElement);
        
    });

    const chatProfiles = document.querySelectorAll('.chat-profile');
    chatProfiles.forEach(profile => {
        profile.classList.remove('is_active');
    });

    // Add active class to the clicked profile
    const clickedProfile = Array.from(chatProfiles).find(profile => {
        const h3 = profile.querySelector('h3');
        return h3 && h3.textContent.includes(name.split('-')[0]);
    });
    
    if (clickedProfile) {
        const threadId = clickedProfile.getAttribute('data-thread-id');
        const unseenCount = document.getElementById(`unseen_count_${threadId}`);
        if (unseenCount) {
            unseenCount.remove(); // Remove the unseen count span by ID
        }
        clickedProfile.classList.add('is_active');
    }
}


function closeChat() {
    document.getElementById('chat-container').style.display = 'none';
}


function newMessage(message, send_by_id) {
    // Convert user_id to a number
    let user_id = parseInt(USER_ID.val(), 10);  

    text = message.trim()

    if (text) {
        const name = document.getElementById('chat-with').textContent;
       // console.log('input: ', chats[name]);
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const messageElement = document.createElement('div');

        if (send_by_id === user_id) {
            messageElement.classList.add('message', 'sent');  
        } else {
            messageElement.classList.add('message', 'received'); 
        }

        messageElement.innerHTML = text + `<span class="time">${time}</span>`;
        document.getElementById('chat-messages').appendChild(messageElement);

        if (!chats[name]) {
            chats[name] = [];
        }
        chats[name].push({ text: text, time: time, type: send_by_id === user_id ? 'sent' : 'received' });

        // Scroll the chat window to the bottom
        const chatMessagesElement = document.getElementById('chat-messages');
        chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;  // Scroll to the bottom of chat
        text = '';  // Clear input
        message = '';
        // Send message data
        const messageData = {
            user: name,
            message: text,
            time: time
        };
        socket.send(JSON.stringify(messageData));

    }
}


socket.onopen = function(e) {
    send_message_form.on('submit', function(e) {
        e.preventDefault();
        let message = inputMessage.val();
        let send_by = parseInt(USER_ID.val(), 10);
        let send_to = otherUserId;
        let thread_id = activeThread;

        let data = {
            'message': message,
            'send_by': send_by,
            'send_to': send_to,
            'thread_id': thread_id
        };
        
       // console.log('data: ', data);
        data = JSON.stringify(data);
    
        // Ensure the WebSocket is open before sending
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(data);
            $(this)[0].reset();
        } else {
            console.log('WebSocket is not open. Message not sent.');
        }
    });

};


socket.onmessage = async function(e) {
    let data = JSON.parse(e.data)
    let message = data['message']
    let send_by_id = data['send_by']
    newMessage(message, send_by_id)
    //console.log('on message', e)
}

socket.onerror = async function(e) {
    console.log('error', e)
}

socket.onclose = async function(e) {
    console.log('close', e)
}

