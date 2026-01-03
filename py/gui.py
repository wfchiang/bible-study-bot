import asyncio
import streamlit as st
from agent import create_agent

# Page configuration
st.set_page_config(page_title="Bible Study Bot", page_icon="📖")
st.title("📖 Bible Study Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question about the Bible..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status_container = st.status("Thinking...", expanded=True)
        message_placeholder = st.empty()

        async def stream_chat():
            agent = await create_agent()
            inputs = {"messages": st.session_state.messages}
            full_response = ""
            
            async for event in agent.astream_events(inputs, version="v2"):
                event_type = event["event"]
                
                if event_type == "on_tool_start":
                    status_container.write(f"**Calling tool:** `{event['name']}`")
                elif event_type == "on_tool_end":
                    status_container.write(f"**Tool output:**")
                    status_container.write(event["data"].get("output"))

                if (event_type == "on_chat_model_stream" and 
                    event["metadata"].get("langgraph_node") == "agent"):
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        print(f">> {chunk.content}")
                        full_response += chunk.content
                        message_placeholder.markdown(full_response + "▌")
            
            status_container.update(label="Finished thinking", state="complete", expanded=False)

            message_placeholder.markdown(full_response)
            return full_response

        try:
            response_content = asyncio.run(stream_chat())
            st.session_state.messages.append({"role": "assistant", "content": response_content})
        except Exception as e:
            st.error(f"An error occurred: {e}")