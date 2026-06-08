from google.cloud import dialogflow_v2 as dialogflow


REQUEST_TIMEOUT = 60


def detect_intent(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient(transport="rest")
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={
            "session": session,
            "query_input": query_input,
        },
        retry=None,
        timeout=REQUEST_TIMEOUT,
    )
    return response.query_result

