
import streamlit as st
from chatbot.chatbot import Chatbot

# Initialize chatbot at startup for faster response times
try:
    chatbot = Chatbot()
    print("Chatbot initialized successfully!")
except Exception as e:
    print(f" Failed to initialize chatbot: {e}")
    chatbot = None

def sidebar_chat():
    with st.sidebar:
        st.title("Chat with Data")
        
        # Show chatbot status
        if chatbot is None:
            st.error("Chatbot is not available. Please check Google Cloud credentials.")
            st.info("Run `gcloud auth application-default login` to set up credentials.")
            return

        # Define a container for the chat history with a fixed height and scrolling
        chat_container = st.container(height=500)

        # Define the function to clear chat history
        def clear_chat_history():
            st.session_state.messages = [{"role": "assistant", "content": "How can I help you analyze the data?"}]
        
        # Add the clear chat button at the top (or bottom, your choice)
        st.button("Clear chat", on_click=clear_chat_history)

        # Initialize session state for messages if it doesn't exist
        if "messages" not in st.session_state:
            clear_chat_history()

        # Capture user input. st.chat_input will always appear at the bottom of the screen.
        if user_message := st.chat_input("Ask questions about the data"):
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
                        response = chatbot.chat(user_message)

                        print("RESPONSE: ", response)

                        # Display the response
                        st.markdown(response)
            
            # Add the chatbot's response to the message history
            st.session_state.messages.append({"role": "assistant", "content": response})
