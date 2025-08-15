
import streamlit as st
from chatbot.chatbot import Chatbot

# Initialize chatbot at startup for faster response times
try:
    st.session_state.chatbot = Chatbot()
    print("Chatbot initialized successfully!")
except Exception as e:
    print(f" Failed to initialize chatbot: {e}")
    st.session_state.chatbot = None

@st.fragment
def sidebar_chat():
        st.title("Chat Assistant")


        
        # Define a container for the chat history with a fixed height and scrolling
        chat_container = st.container(height=450)

        # Define the function to clear chat history
        def clear_chat_history():
            st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]
        
        # Add the clear chat button at the top (or bottom, your choice)
        st.button("Clear chat", on_click=clear_chat_history)

        # Initialize session state for messages if it doesn't exist
        if "messages" not in st.session_state:
            clear_chat_history()

        # Capture user input. st.chat_input will always appear at the bottom of the screen.
        if user_message := st.chat_input("Enter prompt here"):
            # Add user's message to state immediately
            st.session_state.messages.append({"role": "user", "content": user_message})

        # Display all messages from session state inside the container
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Handle the chatbot's response logic
        # Check if the last message was from the user, indicating we need a new response
        if st.session_state.messages[-1]["role"] == "user":
            with chat_container: # Ensure the spinner and response appear in the container
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Call the chatbot

                        if 'chatbot' not in st.session_state:
                            st.session_state.chatbot = Chatbot()

                        response = st.session_state.chatbot.chat(user_message)

                        print("RESPONSE: ", response)

                        if response.startswith("Error"):
                            response = "I'm sorry, I'm having trouble processing your request. Please try again."
                            st.session_state.chatbot = Chatbot()

            
            # Add the chatbot's response to the message history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
