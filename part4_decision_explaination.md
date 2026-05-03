### Question
#### 1. Trade-offs: What trade-offs did you make in Parts 2 and 3? For example, did you prioritize, simplicity over extensibility, or vice versa? Why?
Ans: I prioritize the simplicity first because the validation logic needs to carefully implementation and debugging. If logic is too complex, it's hard to debug if there are problems, bugs.

#### 2. Alternatives: What alternative approaches did you consider for the validation logic? Why did you choose the approach you used?
Ans: Firstly I implement the validation logic in the sigle function because that will be easy to read a flow of process, but I refactor it into small function to make it done in a single purpose. I think this approch is easy to maintain and understanding including the error handling.

#### 3. Debugging process: Walk us through how you analyzed the flawed code in Part 1. What did you look at first? How did you prioritize which issues were most severe?
Ans: Firstly I scan through the code and saw that they use sqlite to be database and see the execution statement code, this is very dangerous to write in this way. 

After this I notice that function does not validate any input arguments, so this will make the above issue highly impact. 

Then I read code carefully to understand what does function do and found vulnerable logic which is function does not care how many customer has in currently. So this will make us to lost profit if we deploy this code.

#### 4. Evolution: If this validation module needed to grow into a production service handling thousands of orders per minute, what would you change about your current design? What would you keep?
Ans: I will reduce database access time to just query once when validation order because this code is access to database multiple times. 

#### 5. Tools: If you used AI tools or other references for any part of this assessment, which parts did you use them for? How did you verify the output was correct?
Ans: I use AI by prompt ask them to research how to use or write in each lib. In coding process I code it by myself. I didn't copy all what AI generated because some code has a bug in that and code does not align to my design. So I read every line of code and make sure that code is run correctly. Including unit test that have to write to cover all case too.
