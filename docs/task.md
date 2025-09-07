# General Information

We’d like to challenge you with a real problem from our environment. We are not only interested in the final result, but also in your approach and thought process: How do you analyze the problem? Which tools do you use? How do you prioritize? Which assumptions do you make?

# Please note:

- It does not have to be perfectly functional or fully automated.
- What matters is that we can follow your reasoning.
- The task is designed to take 3-5 hours.

# Task: Extracting Menu Information from Restaurant Websites

The goal of this exercise is to explore how information can be automatically extracted from websites and structured in a way that we can feed into our internal tool.

# Current manual process

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

# Expected Output

## Per restaurant

- If a cookie banner appears → text of the "accept" button

## Per menu

- Link to the menu on the website
- Menu type (e.g. drinks menu, food menu, daily specials)
- Format of the menu (PDF or screenshot)
- Language of the menu
- If PDF → text of the button to open/download

## Information provided by us

- A list of restaurant websites
- A predefined list of possible menu types
- A predefined list of menu formats

# Deliverables

- Your extracted results for 2–3 example restaurants (JSON, CSV, or another structured format).
- (Optional) Suggestions for how to scale or automate this process further.