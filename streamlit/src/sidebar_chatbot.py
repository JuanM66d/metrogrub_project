
import streamlit as st


def sidebar_chat():
    with st.sidebar:
        st.title("Chat with Data")

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "How can I help you analyze the data?"}]

        messages_container = st.container(height=500)

        with messages_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        def clear_chat_history():
            st.session_state.messages = [{"role": "assistant", "content": "How can I help you analyze the data?"}]

        def call_chatbot(user_message):

            chatbot_response = "test"
            print(chatbot_response)
            st.session_state.messages.append({"role": "assistant", "content": "test response"})

        input_container = st.container()

        with input_container:
            user_message = st.chat_input("Ask questions about the data")
            if user_message:
                st.session_state.messages.append({"role": "user", "content": user_message})
                call_chatbot(user_message)
                st.rerun()

            st.button("Clear chat", on_click=clear_chat_history)