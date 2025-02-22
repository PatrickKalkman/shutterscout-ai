Agents - Guided tour
Open In Colab
Open In Studio Lab
In this guided visit, you will learn how to build an agent, how to run it, and how to customize it to make it work better for your use-case.

Building your agent
To initialize a minimal agent, you need at least these two arguments:

model, a text-generation model to power your agent - because the agent is different from a simple LLM, it is a system that uses a LLM as its engine. You can use any of these options:

TransformersModel takes a pre-initialized transformers pipeline to run inference on your local machine using transformers.
HfApiModel leverages a huggingface_hub.InferenceClient under the hood and supports all Inference Providers on the Hub.
LiteLLMModel similarly lets you call 100+ different models and providers through LiteLLM!
AzureOpenAIServerModel allows you to use OpenAI models deployed in Azure.
tools, a list of Tools that the agent can use to solve the task. It can be an empty list. You can also add the default toolbox on top of your tools list by defining the optional argument add_base_tools=True.

Once you have these two arguments, tools and model, you can create an agent and run it. You can use any LLM you’d like, either through Inference Providers, transformers, ollama, LiteLLM, or Azure OpenAI.

HF Inference API is free to use without a token, but then it will have a rate limit.

To access gated models or rise your rate limits with a PRO account, you need to set the environment variable HF_TOKEN or pass token variable upon initialization of HfApiModel. You can get your token from your settings page

Copied
from smolagents import CodeAgent, HfApiModel

model_id = "meta-llama/Llama-3.3-70B-Instruct" 

model = HfApiModel(model_id=model_id, token="<YOUR_HUGGINGFACEHUB_API_TOKEN>") # You can choose to not pass any model_id to HfApiModel to use a default free model
# you can also specify a particular provider e.g. provider="together" or provider="sambanova"
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

agent.run(
    "Could you give me the 118th number in the Fibonacci sequence?",
)
CodeAgent and ToolCallingAgent
The CodeAgent is our default agent. It will write and execute python code snippets at each step.

By default, the execution is done in your local environment. This should be safe because the only functions that can be called are the tools you provided (especially if it’s only tools by Hugging Face) and a set of predefined safe functions like print or functions from the math module, so you’re already limited in what can be executed.

The Python interpreter also doesn’t allow imports by default outside of a safe list, so all the most obvious attacks shouldn’t be an issue. You can authorize additional imports by passing the authorized modules as a list of strings in argument additional_authorized_imports upon initialization of your CodeAgent:

Copied
model = HfApiModel()
agent = CodeAgent(tools=[], model=model, additional_authorized_imports=['requests', 'bs4'])
agent.run("Could you get me the title of the page at url 'https://huggingface.co/blog'?")
The LLM can generate arbitrary code that will then be executed: do not add any unsafe imports!

The execution will stop at any code trying to perform an illegal operation or if there is a regular Python error with the code generated by the agent.

You can also use E2B code executor instead of a local Python interpreter by first setting the E2B_API_KEY environment variable and then passing use_e2b_executor=True upon agent initialization.

Learn more about code execution in this tutorial.

We also support the widely-used way of writing actions as JSON-like blobs: this is ToolCallingAgent, it works much in the same way like CodeAgent, of course without additional_authorized_imports since it doesn’t execute code:

Copied
from smolagents import ToolCallingAgent

agent = ToolCallingAgent(tools=[], model=model)
agent.run("Could you get me the title of the page at url 'https://huggingface.co/blog'?")
Inspecting an agent run
Here are a few useful attributes to inspect what happened after a run:

agent.logs stores the fine-grained logs of the agent. At every step of the agent’s run, everything gets stored in a dictionary that then is appended to agent.logs.
Running agent.write_memory_to_messages() writes the agent’s memory as list of chat messages for the Model to view. This method goes over each step of the log and only stores what it’s interested in as a message: for instance, it will save the system prompt and task in separate messages, then for each step it will store the LLM output as a message, and the tool call output as another message. Use this if you want a higher-level view of what has happened - but not every log will be transcripted by this method.
Tools
A tool is an atomic function to be used by an agent. To be used by an LLM, it also needs a few attributes that constitute its API and will be used to describe to the LLM how to call this tool:

A name
A description
Input types and descriptions
An output type
You can for instance check the PythonInterpreterTool: it has a name, a description, input descriptions, an output type, and a forward method to perform the action.

When the agent is initialized, the tool attributes are used to generate a tool description which is baked into the agent’s system prompt. This lets the agent know which tools it can use and why.

Default toolbox
Transformers comes with a default toolbox for empowering agents, that you can add to your agent upon initialization with argument add_base_tools = True:

DuckDuckGo web search*: performs a web search using DuckDuckGo browser.
Python code interpreter: runs your LLM generated Python code in a secure environment. This tool will only be added to ToolCallingAgent if you initialize it with add_base_tools=True, since code-based agent can already natively execute Python code
Transcriber: a speech-to-text pipeline built on Whisper-Turbo that transcribes an audio to text.
You can manually use a tool by calling it with its arguments.

Copied
from smolagents import DuckDuckGoSearchTool

search_tool = DuckDuckGoSearchTool()
print(search_tool("Who's the current president of Russia?"))
Create a new tool
You can create your own tool for use cases not covered by the default tools from Hugging Face. For example, let’s create a tool that returns the most downloaded model for a given task from the Hub.

You’ll start with the code below.

Copied
from huggingface_hub import list_models

task = "text-classification"

most_downloaded_model = next(iter(list_models(filter=task, sort="downloads", direction=-1)))
print(most_downloaded_model.id)
This code can quickly be converted into a tool, just by wrapping it in a function and adding the tool decorator: This is not the only way to build the tool: you can directly define it as a subclass of Tool, which gives you more flexibility, for instance the possibility to initialize heavy class attributes.

Let’s see how it works for both options:

Copied
from smolagents import tool


def model_download_tool(task: str) -> str:
    """
    This is a tool that returns the most downloaded model of a given task on the Hugging Face Hub.
    It returns the name of the checkpoint.

    Args:
        task: The task for which to get the download count.
    """
    most_downloaded_model = next(iter(list_models(filter=task, sort="downloads", direction=-1)))
    return most_downloaded_model.id
The function needs:

A clear name. The name should be descriptive enough of what this tool does to help the LLM brain powering the agent. Since this tool returns the model with the most downloads for a task, let’s name it model_download_tool.
Type hints on both inputs and output
A description, that includes an ‘Args:’ part where each argument is described (without a type indication this time, it will be pulled from the type hint). Same as for the tool name, this description is an instruction manual for the LLM powering you agent, so do not neglect it. All these elements will be automatically baked into the agent’s system prompt upon initialization: so strive to make them as clear as possible!
This definition format is the same as tool schemas used in apply_chat_template, the only difference is the added tool decorator: read more on our tool use API here.

Then you can directly initialize your agent:

Copied
from smolagents import CodeAgent, HfApiModel
agent = CodeAgent(tools=[model_download_tool], model=HfApiModel())
agent.run(
    "Can you give me the name of the model that has the most downloads in the 'text-to-video' task on the Hugging Face Hub?"
)
You get the following logs:

Copied
╭──────────────────────────────────────── New run ─────────────────────────────────────────╮
│                                                                                          │
│ Can you give me the name of the model that has the most downloads in the 'text-to-video' │
│ task on the Hugging Face Hub?                                                            │
│                                                                                          │
╰─ HfApiModel - Qwen/Qwen2.5-Coder-32B-Instruct ───────────────────────────────────────────╯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 0 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
╭─ Executing this code: ───────────────────────────────────────────────────────────────────╮
│   1 model_name = model_download_tool(task="text-to-video")                               │
│   2 print(model_name)                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
Execution logs:
ByteDance/AnimateDiff-Lightning

Out: None
[Step 0: Duration 0.27 seconds| Input tokens: 2,069 | Output tokens: 60]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Step 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
╭─ Executing this code: ───────────────────────────────────────────────────────────────────╮
│   1 final_answer("ByteDance/AnimateDiff-Lightning")                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
Out - Final answer: ByteDance/AnimateDiff-Lightning
[Step 1: Duration 0.10 seconds| Input tokens: 4,288 | Output tokens: 148]
Out[20]: 'ByteDance/AnimateDiff-Lightning'
Read more on tools in the dedicated tutorial.

Multi-agents
Multi-agent systems have been introduced with Microsoft’s framework Autogen.

In this type of framework, you have several agents working together to solve your task instead of only one. It empirically yields better performance on most benchmarks. The reason for this better performance is conceptually simple: for many tasks, rather than using a do-it-all system, you would prefer to specialize units on sub-tasks. Here, having agents with separate tool sets and memories allows to achieve efficient specialization. For instance, why fill the memory of the code generating agent with all the content of webpages visited by the web search agent? It’s better to keep them separate.

You can easily build hierarchical multi-agent systems with smolagents.

To do so, encapsulate the agent in a ManagedAgent object. This object needs arguments agent, name, and a description, which will then be embedded in the manager agent’s system prompt to let it know how to call this managed agent, as we also do for tools.

Here’s an example of making an agent that managed a specific web search agent using our DuckDuckGoSearchTool:

Copied
from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool, ManagedAgent

model = HfApiModel()

web_agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

managed_web_agent = ManagedAgent(
    agent=web_agent,
    name="web_search",
    description="Runs web searches for you. Give it your query as an argument."
)

manager_agent = CodeAgent(
    tools=[], model=model, managed_agents=[managed_web_agent]
)

manager_agent.run("Who is the CEO of Hugging Face?")
For an in-depth example of an efficient multi-agent implementation, see how we pushed our multi-agent system to the top of the GAIA leaderboard.

Talk with your agent and visualize its thoughts in a cool Gradio interface
You can use GradioUI to interactively submit tasks to your agent and observe its thought and execution process, here is an example:

Copied
from smolagents import (
    load_tool,
    CodeAgent,
    HfApiModel,
    GradioUI
)

# Import tool from Hub
image_generation_tool = load_tool("m-ric/text-to-image", trust_remote_code=True)

model = HfApiModel(model_id)

# Initialize the agent with the image generation tool
agent = CodeAgent(tools=[image_generation_tool], model=model)

GradioUI(agent).launch()
Under the hood, when the user types a new answer, the agent is launched with agent.run(user_request, reset=False). The reset=False flag means the agent’s memory is not flushed before launching this new task, which lets the conversation go on.

You can also use this reset=False argument to keep the conversation going in any other agentic application.\