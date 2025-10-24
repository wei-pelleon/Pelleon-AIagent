Now, let's create this code base:

First, you need to find the following:
1. for each window type (MARK), the windows unit cost from RSmeans data;
2. for each door type (MARK), the interior door unit cost from Rsmeans data. Note there is only one exterior door which is balcony; and all others are interior doors.
3. for each appliance type, the unit cost from Rsmeans data.

There is a high chance that you can not find the exact match for a material needed; However, try to find the best match that aligns with dimensions, material type, finishes, etc as close as possible, and use the best match's cost as the material's cost.

After each type's cost is determined, you save them and note them down using a table, showing the original material ID, the selected material's ID in Rsmeans data, and the material cost, installation cost, and total cost, for the material type.

Second, you need to calculate the total cost for each category:
1. total cost for window;
2. total cost for door;
3. total cost for appliance.

Third, you need to take the best match from Rsmeans, and obtain a list of top 3 alternatives for each best match. 
When you find the match, you follow the rules below:
1. for window, you make sure the window's dimensions are similar in area; and you need to keep the style for the windows;
2. for exterior door: you make sure materials are as close as possible; keep the type; keep the width fixed; the candidates' height should be taller thant 7'. 
3. for appliances, you make sure that we can apply a uniform 10% cost reduction on all appliances. No candidates needed.


Fourth, once you found the top 3 alternatives for each best match (if possible), you need to use LLM to judge on the following three criteria:
1. functional deviation from original material, from 1-5, 5 means limited deviation and most faithfulness to original function; 1 means extreme deviation.
2. design deviation from original material, from 1-5, 5 means limited deviation and most faithfulness to original design intent; 1 means extreme deviation of design intent.
3. the cost reduction. from 1-5, 5 means the price reduction is highest; and 1 means the price reduction is limited. Let's say 5 is the reduction of 30%+, 4 is reduction of 20%+, 3 is 15%+, 2 is 10%+, and 1 is the reduction of 5%. Don't find alternatives that are more expensive than the original material.

Try to pick the top alternatives that stays close in functional and design, but has most cost reduction.

Note for appliances, we can apply a uniform 10% reduction on all materials. The functional, design are all the same, i.e. 5. and the cost reduction is 2. 


Five, once you obtained those metrics, you need to note down the candidates for each material type, and the functional deviation, design deviation, and cost reduction, as three additional columns. 

Six, let's write an algorithm to evaluate each alternative and aggregate the choices, and get the total cost reduction, total average functional deviation, total average design deviation.

Seven, you need to show a UI, and give three choices: best functional deviation while having best cost reduction; best cost reduction regardless of functional and design intent impact, best average design while having best cost reduction, and balanced (1/3 weight for each criteria). For each chioce, you can see the functional aveerage, design average, and cost reduction scores.
You can also see the breakdown by material type: 
window function average, window design average, window cost reduction;
door function average, door design average, door cost reduction;
appliance function average, appliance design average, appliance cost reduction. 


Let's make sure we keep the code MVP really simple. Don't complicate things.
Do it one step, one tsv/csv at a time. Test frequently to see if the input/output is correct until you move on to the next step. Make sure you test everything as frequent as possible. Keep all your test codes in test/ folder. Keep the test names simple, and name the same as the python filename that you would create in agent/ folder. Try to make the python files small, intuitive, and self-contained. Good to have small python files that has focused, elegant and simple code, and main function for simple testing. 

You need to use temporal to orchastrate the processes. The data that got generated will be saved in data/processed/ folder. Try to make the names intuitive and aligned with existing tables / data, for readability. 

Produce a .md file describing the connection between data and python code.


