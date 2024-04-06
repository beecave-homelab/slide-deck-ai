import logging
import pathlib
import random
import tempfile
from typing import List

import json5
import streamlit as st
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

from global_config import GlobalConfig
from helpers import llm_helper, pptx_helper

APP_TEXT = json5.loads(open(GlobalConfig.APP_STRINGS_FILE, 'r', encoding='utf-8').read())
# langchain.debug = True
# langchain.verbose = True

logger = logging.getLogger(__name__)
progress_bar = st.progress(0, text='Setting up SlideDeck AI...')


def display_page_header_content():
    """
    Display content in the page header.
    """

    st.title(APP_TEXT['app_name'])
    st.subheader(APP_TEXT['caption'])
    st.markdown(
        'Powered by'
        ' [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)'
    )


def display_page_footer_content():
    """
    Display content in the page footer.
    """

    st.text(APP_TEXT['tos'] + '\n\n' + APP_TEXT['tos2'])
    # st.markdown(
    #     '![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fhuggingface.co%2Fspaces%2Fbarunsaha%2Fslide-deck-ai&countColor=%23263759)'  # noqa: E501
    # )


def build_ui():
    """
    Display the input elements for content generation.
    """

    display_page_header_content()

    with st.expander('Usage Policies and Limitations'):
        display_page_footer_content()

    progress_bar.progress(50, text='Setting up chat interface...')
    set_up_chat_ui()


def set_up_chat_ui():
    """
    Prepare the chat interface and related functionality.
    """

    history = StreamlitChatMessageHistory(key='chat_messages')
    llm = llm_helper.get_hf_endpoint()

    with open(GlobalConfig.CHAT_TEMPLATE_FILE, 'r', encoding='utf-8') as in_file:
        template = in_file.read()

    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | llm

    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: history,  # Always return the instance created earlier
        input_messages_key='question',
        history_messages_key='chat_history',
    )

    with st.expander('Usage Instructions'):
        st.write(GlobalConfig.CHAT_USAGE_INSTRUCTIONS)

    st.chat_message('ai').write(
        random.choice(APP_TEXT['ai_greetings'])
    )

    for msg in history.messages:
        # st.chat_message(msg.type).markdown(msg.content)
        st.chat_message(msg.type).code(msg.content, language='json')

    progress_bar.progress(100, text='Done!')
    progress_bar.empty()

    if prompt := st.chat_input(
        placeholder=APP_TEXT['chat_placeholder'],
        max_chars=GlobalConfig.LLM_MODEL_MAX_INPUT_LENGTH
    ):
        logger.debug('User input: %s', prompt)
        st.chat_message('user').write(prompt)

        progress_bar_pptx = st.progress(0, 'Calling LLM...')

        # As usual, new messages are added to StreamlitChatMessageHistory when the Chain is called
        config = {'configurable': {'session_id': 'any'}}
        response: str = chain_with_history.invoke({'question': prompt}, config)
        st.chat_message('ai').markdown('```json\n' + response)

        # The content has been generated as JSON
        # There maybe trailing ``` at the end of the response -- remove them
        # To be careful: ``` may be part of the content as well when code is generated
        str_len = len(response)
        response_cleaned = response

        progress_bar_pptx.progress(50, 'Analyzing response...')

        try:
            idx = response.rindex('```')
            logger.debug('str_len: %d, idx of ```: %d', str_len, idx)

            if idx + 3 == str_len:
                # The response ends with ``` -- most likely the end of JSON response string
                response_cleaned = response[:idx]
            elif idx + 3 < str_len:
                # Looks like there are some more content beyond the last ```
                # In the best case, it would be some additional plain-text response from the LLM
                # and is unlikely to contain } or ] that are present in JSON
                if '}' not in response[idx + 3:]:  # the remainder of the text
                    response_cleaned = response[:idx]
        except ValueError:
            # No ``` found
            pass

        # Now create the PPT file
        progress_bar_pptx.progress(75, 'Creating the slide deck...give it a moment')
        generate_slide_deck(response_cleaned, pptx_template='Blank')
        progress_bar_pptx.progress(100, text='Done!')


def generate_slide_deck(json_str: str, pptx_template: str) -> List:
    """
    Create a slide deck.

    :param json_str: The content in *valid* JSON format.
    :param pptx_template: The PPTX template name.
    :return: A list of all slide headers and the title.
    """

    # # Get a unique name for the file to save -- use the session ID
    # ctx = st_sr.get_script_run_ctx()
    # session_id = ctx.session_id
    # timestamp = time.time()
    # output_file_name = f'{session_id}_{timestamp}.pptx'

    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pptx')
    path = pathlib.Path(temp.name)

    logger.info('Creating PPTX file...')
    all_headers = pptx_helper.generate_powerpoint_presentation(
        json_str,
        slides_template=pptx_template,
        output_file_path=path
    )

    with open(path, 'rb') as f:
        st.download_button('Download PPTX file ⇩', f, file_name='Presentation.pptx')

    return all_headers


def main():
    """
    Trigger application run.
    """

    build_ui()


if __name__ == '__main__':
    main()
