
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
                    # Create placeholders for progress and details
                    progress_placeholder = st.empty()
                    details_expander = st.expander("Show processing details", expanded=False)
                    details_placeholder = details_expander.empty()
                    
                    # Initialize progress tracking
                    current_progress = "Analyzing your question..."
                    progress_steps = []
                    
                    try:
                        if 'chatbot' not in st.session_state:
                            st.session_state.chatbot = Chatbot()

                        # Get the streaming response from chatbot
                        response_stream = st.session_state.chatbot.chat(user_message)
                        
                        # Process each progress update
                        for update in response_stream:
                            if update["type"] == "progress":
                                current_progress = update["message"]
                                if "details" in update:
                                    progress_steps = update["details"]
                                
                                # Update the progress display
                                progress_placeholder.info(current_progress)
                                
                                # Update details if available
                                if progress_steps:
                                    details_text = "\n".join([f"✓ {step}" for step in progress_steps])
                                    details_placeholder.markdown(details_text)
                                
                            elif update["type"] == "complete":
                                # Show final response
                                progress_placeholder.success("✅ Analysis complete!")
                                response = update["message"]
                                
                                # Update final details
                                if "details" in update and update["details"]:
                                    final_details = "\n".join([f"✓ {step}" for step in update["details"]])
                                    details_placeholder.markdown(f"{final_details}\n\n**Final Response:**\n{response}")
                                else:
                                    details_placeholder.markdown(f"**Final Response:**\n{response}")
                                
                            elif update["type"] == "error":
                                progress_placeholder.error("❌ Error occurred")
                                response = update["message"]
                                details_placeholder.error(f"Error: {response}")
                                
                    except Exception as e:
                        progress_placeholder.error("❌ Error occurred")
                        response = "I'm sorry, I'm having trouble processing your request. Please try again."
                        details_placeholder.error(f"Exception: {str(e)}")
                        st.session_state.chatbot = Chatbot()

                    print("RESPONSE: ", response)
            
            # Add the chatbot's response to the message history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
