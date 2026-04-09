# FitShopAssistant
An AI Shopping Assistant That Will Help You Buy The Best Meals For You Based On Your Macros.

How It Works -- First Time User:
1. Open The Application For The First Time
2. Create A Profile: Name, Age, Height, Weight, Overall Goal, Calorie Goal, Macro's Goal
3. Log Food Throughout The Day
4. Log Exercises Throughout The Day
5. Uses OpenFoodFacts Production For Nutritional Information
6. Uses https://github.com/yuhonas/free-exercise-db For Exercise Information
7. Local Ollama llama3 AI recommends meals to make based on logged macros, AI fetches Users Local Walmart Prices (settings include but are not limited to; Low Cost, Easy/Fast to make)
8. In Settings User Can Type What Cookware They Have So the AI can Recommend more accurately.
9. User Can Define AI Strictness In settings, Basically; Less Strict = More loose on Cookware: i.e User Says They Have A Stove, AI Assumes User Also Has A Pan. More Strict; Strictly Adhears to Specified Cookware: i.e User Says They Have A Stove, AI Assumes User ONLY Has a Stove. Mid Strict; A nice middleground between Less and More Strict
