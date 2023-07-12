import os
from apikey import apikey

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory

os.environ['OPENAI_API_KEY'] = apikey

# Prompt
prompt = input('Write your prompt here: ')
topic = 'GitHub'

# Prompt templates
title_template = PromptTemplate(
    input_variables=['topic'],
    template='Tell me which repositories is the most technically complex {topic}'
)

script_template = PromptTemplate(
    input_variables=['title'],
    template='Tell me which repositories is the most technically complex and provide a link for the complex repository TITLE: {title}'
)

# Memory
title_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history')
script_memory = ConversationBufferMemory(input_key='title', memory_key='chat_history')

# Llms
llm = OpenAI(temperature=0.9)
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)
script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True, output_key='script', memory=script_memory)

# Run the chains
if prompt:
    title = title_chain.run(prompt)
    script = script_chain.run(title=title)

    print(title)
    print(script)

    print('Title History:')
    print(title_memory.buffer)

    print('Script History:')
    print(script_memory.buffer)
