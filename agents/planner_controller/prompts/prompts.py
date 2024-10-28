class PlannerPrompt():
    def __init__(self, index_examples=list(range(7)), goal= None, last_steps=[], steps_failed=[]):
        self.system_prompt= f"""
    You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your tasks 
    as the Planner is to figure out the different steps required to complete a certain goal. You are an expert in navigating the internet and any web page possible.
    You have a screenshot of the state of the page as well as the steps executed.
    """
        example1= f"""-Example 
If the goal is "Open New York Times page" \n

Your answer should be:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
1. Open New York Times website
</plan>
<thought>
Reasoning for the plan
</thought>

"""
        example2=f"""-Example 

If the goal is "Find a silver Rolex for men priced between $13,000 and $15,000 on Ebay"

Your answer should be:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
1. Open ebay website
2. Search for men’s watches.
3. Filter results by the Rolex brand 
4. Apply color filter to grey 
5. Apply price filter from 13,000 to 15,000
6. Pick first watch that appears after filtering 
7. Provide the results to the user
</plan>
<thought>
Reasoning for the plan
</thought>

"""
        example3=f"""-Example 

If the goal is "Retrieve the second section of the first article related to 'Trading for beginners' on Investopedia"

Your answer should be:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
1. Open the Investopedia website.
2. Search for articles on ”Trading for beginners.”
3. Review the first three articles.
4. Open the first article.
5. Retrieve and provide the content of the second section to user.
</plan>
<thought>
Reasoning for the plan
</thought>

"""
        example4=f"""-Example 
If the goal is "Get me the amount of views in the most trending video right now on Youtube"

Your answer should be:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
1. Open Youtube website
2. Click on Trending
3. Rertrieve the total number of views in the first video
</plan>
<thought>
Reasoning for the plan
</thought>

"""
        example5=f"""Example 
If the goal is "Find the best selling products of 2022"

Your answer should be:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
1. Explore page to find relevant section related to reports on best selling products
2. Filter products by year 2022
3. Provide product with most sales
</plan>
<thought>
Reasoning for the plan
</thought>

"""
        example6=f"""Example 
If the goal is "Find the customer's mail associated with the name Jane Doe"

Your answer should be:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
1. Explore page to find relevant section related to customer's information
2. Filter by name Jane Doe
3. Retrieve Jane Doe's email 
</plan>
<thought>
Reasoning for the plan
</thought>

"""
        example7= f"""Example 
If the goal is "Summarize the second news article in the Life section of the Irish Independent"

Your answer should be:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
1. Open the Irish Independent website
2. Navigate to the Life section
3. Open the second article 
4. Read and summarize the content and provide it to user
</plan>
<thought>
Reasoning for the plan
</thought>

"""
        examples=[example1,example2,example3,example4,example5,example6,example7]
        self.prompt= f"""
Based on the screenshot create a very highlevel plan with intermediate subgoals to achieve the user's final goal. Provide a chain of thought/reasoning of your answer.
Please update your plan depending on the information provided in the Screenshot.

Here are some examples of what is your expected behavior:

""" 
        for i in index_examples:
            self.prompt+=examples[i]

        self.prompt+= f"""End of examples.

Make sure to give your answer in the expected format.

The user's goal is: {goal}

You have executed succesfully the following actions: {last_steps}

These steps have not been succesfully exectued: {steps_failed} 

Please create a more decomposed plan in order to complete the failed steps.

If the goal is complete please return an empty plan.
"""

        
        
        

        
    