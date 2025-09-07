# Task
## General Information

We’d like to challenge you with a real problem from our environment. We are not only interested in the final result, but also in your approach and thought process: How do you analyze the problem? Which tools do you use? How do you prioritize? Which assumptions do you make?

## Please note:

- It does not have to be perfectly functional or fully automated.
- What matters is that we can follow your reasoning.
- The task is designed to take 3-5 hours.

## Task: Extracting Menu Information from Restaurant Websites

The goal of this exercise is to explore how information can be automatically extracted from websites and structured in a way that we can feed into our internal tool.

## Current manual process

1. Open the restaurant’s website.
2. Check if there is a cookie banner.
    - If yes: note the label of the button used to accept cookies.
3. Search for food and drink menus.
4. For each menu found, define the following properties:
    - Menu type (e.g. food menu, drinks menu, daily specials, etc.)
    - Format:
        - PDF
        - Screenshot/Image
    - Language availability: is the menu provided in multiple languages?

## Expected Output

### Per restaurant

- If a cookie banner appears → text of the "accept" button

### Per menu

- Link to the menu on the website
- Menu type (e.g. drinks menu, food menu, daily specials)
- Format of the menu (PDF or screenshot)
- Language of the menu
- If PDF → text of the button to open/download

## Information provided by us

- A list of restaurant websites
- A predefined list of possible menu types
- A predefined list of menu formats

## Deliverables

- Your extracted results for 2–3 example restaurants (JSON, CSV, or another structured format).
- (Optional) Suggestions for how to scale or automate this process further.

# Solution 
You need to provide several solutions (don't implement yet, just let's discuss them!) to this problem or challenge mine.

My thinking is that since the problem is ambigious - different restaurants have different web sites, different structure of the websites, different menu structure, different sections of the menu etc., regular scrape-and-parse approach won't work or will be too complicated at scale.

## Solution 1 (Bootstrap): 
Hire a very cheap team in India or countries alike, which will be regularly and manually going through the list of websites (obtained from yelp, google maps etc.), and compose requested information.

**Pros:**
+ low initial setup costs - no need for complex infrastructure upfront
+ flexibility: can handle any site structure
+ flexibility: input/output formats
+ high quality initial dataset (100-200 sites)
+ deep insight into edge cases

**Cons:**
- doesn't scale well (e.g. refresh restaurants data daily, update a large sets of restaurants)
- error-prone (human factor)
- hard to refresh frequently

## Solution 2 (monolithic AI Agent for crawling and parsing)
Build an AI agent, which does the task:
- gets the list of websites (input file - dynamic, can be updated often)
- crawls the list of websites
- parses fetched pages and looks for the cookies button and the menu links
- parses the menu
- prepares the requested output (static, updates are part of the development workflow) based on the collected and processed information.

**Pros**:
- scalable, but limited to AI's ability to handle diverse websites
- medium-high, depeneds on AI's accuracy (which we may not have contorl on, especially if the AI is external and has own release cycles)
- extendable, possible to enhance the collected information with new properties and features

**Cons**:
- new tech: costs change all the time, the budget is approximate only
- new tech: a steap learning curve

## Solution 3 (Straight ChatGPT)
Prepare a prompt close to what was given and feed the request to ChatGPT. It will parse the websites, and do all the work.

**Pros**
- simplest and fastest in terms of the implementation
+ flexibility: better then pure coding heuristics, but still can't compete with a team of humans
+ flexibility: input/output formats (understands the instructions and can prepare the output based on a sample)

**Cons**
- doesn't scale (slow, epxensive, lacks fine-grained control and error handling)
- no control on the model's life cycle (new releases and respective prompt changes etc) - it can break at the most important moment
- not absolutely reliable - hallucinations are still possible

## Solution 4 (Old good coding and heuristics)
Writing scripts to parse restaurants websites. The idea behind is the the vast majority of restaurants sites based on WordPress/Shopify/Wix etc., and with more or less simple heuristics we'd be aiming to build a unified solution to find and follow the requested links.

**Pros**:
- Regular engineering work, no additional knowledge needed

**Cons**:
- <strike>can with worms</strike> maintenance nightmare: there are always exceptions which should be handled manually - e.g. React based websites, which must be rendered on the client side, different localities of the links etc.
   - Potentially it can be outsourced, but the code will become terrible and not maintenable with the time.
   - Pareto principle - engineers will spend 80% of their time supporting 20% of the scraper corner cases

## Solution 5 (Hybrid)
Modular architecture that combines tranditional coding, AI Agent, Human intervention in the most complicated cases.

- Orchestration: The entire pipeline is orchestrated by n8n or AirFlow
- Crawler module: fetches website content, detects cookie banners, collects all links (we can limit the nested levels to 2)
- Links calssification using a model (either fine-tuned one or something like OpenAI-OSS for starters). The model produces a list of probably menu links with the confidence score per link.
- Verification: for each link, visits link and checks its format
- Escalation: undetected or results with low confidence score cases to be escalated to humans and handled separately. Findings can be baked into Link Classification module.

**Pros**: 
- scalable: an LLM should handle a varienty of disperate use cases, including different languages, non-trivial menu links like "our deserts today"
- scalable: modular architecture allows for module replacement or extension or running on different infra

**Cons**:
- additional effort for fine-tuning (we can start from manual 1000 restaurants and then constantly extend it, still can be outsourced)