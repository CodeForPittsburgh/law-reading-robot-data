
from transformers import GPT2TokenizerFast
import re
import callgpt as gt
import openai

# OpenAI API key
api_key = ''


MAX_TOKENS = 4096
 
## splits the long text into chunks of 4096 tokens
def convert_full_text_to_chunks(full_text):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2") # Initializes a fast GPT-2 tokenizer from the "gpt2"model.

    sentences = re.split(r'(?<=[.!?])\s+', full_text)     # Matches spaces after [.!?] for sentence splitting.
    chunks = []
    current_chunk = []
    current_token_length = 0

    for sentence in sentences:
        token_length = len(tokenizer(sentence)["input_ids"])
        if current_token_length + token_length <= MAX_TOKENS:
            current_chunk.append(sentence)
            current_token_length += token_length
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_token_length = token_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

## gets summaries for all the chunks and joins them to get final gpt summary
def get_gpt_summary(chunks):
    max_out_tokens = 300/len(chunks)
    gpt_summary = ""
    for chunk in chunks:
        prompt = f"""
        Your task is to generate a short summary of the bill \ 
        from state legislation. 

        Summarize the portion of the bill below in at most {max_out_tokens} words. 

        Review: ```{chunk}```
        """
        chunk_summary = get_completion(prompt)
        gpt_summary += str(chunk_summary) +' '

        prompt = f"""
        Your task is to generate a short summary of the bill \ 
        from state legislation. 

        Summarize the bill below in at most 300 words. 

        Review: ```{gpt_summary}```
        """
        summary = get_completion(prompt)


    return gpt_summary


#helper function to use gpt prompt
def get_completion(prompt, model="gpt-3.5-turbo"):
    openai.api_key = api_key
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        n = 1, # Number of responses to generate
        temperature=0, #  generates the same output for the same input prompt every time 
    )
    return response.choices[0].message["content"]
