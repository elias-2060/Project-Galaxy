import React, { ElementType, useEffect, useRef, useState } from "react";
import "../styles/ChatBox.css";
import { JSX } from "react/jsx-runtime";
import axios, { AxiosResponse } from "axios";

const API_URL = import.meta.env.VITE_API_URL;
interface Props {
  isRendered: boolean;
}

const ChatBox = ({ isRendered }: Props) => {
  const [message, setMessage] = useState<string>("");

  type Message = {
    message_id: string;
    user_id: string;
    user_name: string;
    race_id: string;
    position: number;
    message: string;
  };

  const [messages, setMessages] = useState<Message[]>();
  const [selfUser, setUser] = useState<any>();

  const handleSendMessage = () => {
    axios
      .post<any, AxiosResponse<Message>>(
        `${API_URL}/race/chat`,
        { message: message },
        { withCredentials: true }
      )
  };

  const first_render = useRef(true);

  useEffect(() => {
    if (!first_render.current) return;
    first_render.current = false;
    axios // request all mesages
      .get<any, AxiosResponse<{ messages: Message[] }>>(
        `${API_URL}/race/chat`,
        { withCredentials: true }
      )
      .then((response) => {
        setMessages(response.data.messages.reverse());
      });

    axios // request logged in user
      .get(`${API_URL}/user`, { withCredentials: true })
      .then((response) => setUser(response.data));
  }, []);

  const handleSendPressed = async () => {
    if (message !== "") handleSendMessage();
    setMessage("");
  };

  const refreshMessages = () => {
    axios
      .get<any, AxiosResponse<{ messages: Message[] }>>(
        `${API_URL}/race/chat`,
        { withCredentials: true }
      )
      .then((response) => {
        setMessages(response.data.messages.reverse());
      });
  };

  const [triggerMessageRefresh, setTimeLeft] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => {
      console.log("rendered", triggerMessageRefresh);
      setTimeLeft(!triggerMessageRefresh); // Decrease time by 1 second
      refreshMessages();
    }, 1000);
  }, [triggerMessageRefresh]);

  return (
    <div className="chatbox">
      <div className="messages">
        {messages
          ? messages.map((message, index) => {
              if (!selfUser) return null;
              return message.user_id === selfUser.user_id ? (
                <div className="own-message" key={index}>
                  <div className="username">You:</div>
                  <div className="message">{message.message}</div>
                </div>
              ) : (
                <div className="other-message" key={index}>
                  <div className="username">{message.user_name}:</div>
                  <div className="message">{message.message}</div>
                </div>
              );
            })
          : null}
      </div>

      <div className="input-area2">
        <div className="input-area-input">
          <input
            type="text"
            placeholder="Type your message"
            value={message}
            className="input-area"
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              e.key === "Enter" && handleSendPressed();
            }}
          />
        </div>
        <div className="input-area-button">
          <button
            onClick={() => {
              handleSendPressed();
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;
