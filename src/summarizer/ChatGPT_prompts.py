import openai
import tiktoken


def get_system_instructions():
    return "Limit responses to 200 words." \
        "Stay neutral." \
        "When reading a bill, do not overlook small but materially important details such as a single sentence that allocates a large amount of money to a single project"


def get_tagging_prompt(tags, text):
    return "Please examine the following text from the Pennsylvania State Legislature and provide up to 5 of the " \
           "following tags that you think best describe the text: \n\n" + text + "\n\n" + "Tags: " + ", ".join(tags) \
           + "\n\n" + "Text: "


def get_summary_prompt(text):
    return "Please provide a summary of the following text of a Bill from the Pennsylvania State Legislature: \n\n" + text


def get_revision_change_prompt(revision1, revision2):
    return "I am about to provide you with two versions of the same Bill from the Pennsylvania State Legislature. The " \
           "first is the preceding version, and the second is the new version. Please summarize how the text has " \
           "changed from the first to the second: \n\n Preceding Version:" + revision1 + "\n\n New Version: " + \
           revision2

# function from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb
# that counts tokens


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_message = 4
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def generate_messages(request_type, bill_text=None, tags=None, revision1=None, revision2=None):
    messages = [
        {"role": "system", "content": get_system_instructions()},
        # commented out for now but could be useful to provide useful example summaries of what we want as summaries for bills we have good summaries for.
        # REPEAT EACH SECTION AS NEEDED SO THAT CHATGPT IS CONDITIONED TO PROVIDE THE RIGHT REPSONSES
        # {"role": "system", "name":"example_user", "content": INSERT BILL TO SUMMARIZE},
        # {"role": "system", "name": "example_assistant", "content": INSERT EXPECTED SUMMARY},
        # {"role": "system", "name":"example_user", "content": INSERT REVISIONS TO COMPARE},
        # {"role": "system", "name": "example_assistant", "content": INSERT REVISION COMPARISON SUMMARY},
        # {"role": "system", "name":"example_user", "content": BILL TO TAG},
        # {"role": "system", "name": "example_assistant", "content": INSERT TAGS THAT BILL SHOULD BE TAGGED WITH},
    ]
    if request_type == "bill_summary":
        messages += [{"role": "user",
                      "content": get_summary_prompt(bill_text)}]
    elif request_type == "revision_summary":
        messages += [{"role": "user",
                      "content": get_revision_change_prompt(revision1, revision2)}]
    elif request_type == "bill_tags":
        messages += [{"role": "user",
                      "content": get_tagging_prompt(tags, bill_text)}]
    else:
        raise NotImplementedError(
            f"Did not recognize request_type: {request_type}. request_type should be one of: bill_summary, revision_summary, bill_tags")
    # will work when api key is set at environment variable OPENAI_API_KEY. For now just checking that messages generate properly

    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo-0613",
    #     messages=[
    #         {"role": "system", "content": get_system_instructions()},
    #         # commented out for now but could be useful to provide useful example summaries of what we want as summaries for bills we have good summaries for.
    #         # {"role": "system", "name":"example_user", "content": INSERT BILL TO SUMMARIZE},
    #         # {"role": "system", "name": "example_assistant", "content": INSERT EXPECTED SUMMARY},
    #         # {"role": "system", "name":"example_user", "content": INSERT REVISIONS TO COMPARE},
    #         # {"role": "system", "name": "example_assistant", "content": INSERT REVISION COMPARISON SUMMARY},

    #     ],
    #     temperature=0,
    # )
    # return response["choices"][0]["message"]["content"]
    return messages


def get_chatgpt_response(model, messages, temperature):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response["choices"][0]["message"]["content"]
