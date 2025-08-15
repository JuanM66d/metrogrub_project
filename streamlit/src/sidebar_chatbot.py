
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
        
        # Initialize processing flag if it doesn't exist
        if "processing_response" not in st.session_state:
            st.session_state.processing_response = False

        # Capture user input. st.chat_input will always appear at the bottom of the screen.
        if user_message := st.chat_input("Enter prompt here"):
            # Add user's message to state immediately
            st.session_state.messages.append({"role": "user", "content": user_message})
            st.session_state.processing_response = True

        # Display all messages from session state inside the container
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"]) 
            
            # Handle the chatbot's response logic inside the container
            # Check if we need to process a new response
            if st.session_state.processing_response and st.session_state.messages[-1]["role"] == "user":
                # Get the user message
                user_message = st.session_state.messages[-1]["content"]
                
                # Render a single assistant bubble with a spinner first, then replace with the final response
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    with st.spinner("Thinking..."):
                        # Call the chatbot
                        if 'chatbot' not in st.session_state:
                            st.session_state.chatbot = Chatbot()

                        response = st.session_state.chatbot.chat(user_message)

                        print("RESPONSE: ", response)

                        if response.startswith("Error"):
                            response = "I'm sorry, I'm having trouble processing your request. Please try again."
                            st.session_state.chatbot = Chatbot()
                    
                    # Replace spinner with the final response inside the same assistant bubble
                    response_placeholder.markdown(response)
                
                # Add the chatbot's response to the message history AFTER displaying
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Mark as processed
                st.session_state.processing_response = False
            
