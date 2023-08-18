# Speaker for the Dead

## GPT 3 API with vector database

The folder `src` contains implementation of Mark Twain and Mark Billinghurst (coincidentally both Marks).

- Mark Twain was created by putting his biography in a vector database.
- Mark Billinghurst was created by putting his UoA bio, UniSA bio, ECL bio and his wikipedia page in a vector database.
  - Putting academic papers written by Mark is under development.

## Integration with other components of Speaker for the Dead
The code is written in OOP so you do not need to understand the vector DB implementation details to use it when expanding upon this.

For example, if you were to use Mark Billinghurst's character:

To get a single response:
```python
from src.MarkBillinghurst import MarkBillinghurst

MB = MarkBillinghurst()
output = MB.converse('Hi, my name is Nikhil, who is this?')
print(output)
```

```
'Hi Nikhil, I am Mark Billinghurst. I am a computer interface technology researcher and I specialize in augmented reality (AR) technology. I have published over 650 research papers and I am a Fellow of the IEEE.'
```

If you keep using the method `converse`, previous conversation is automaticaly saved:

```python
output2 = MB.converse('What is my name?')
print(output2)
```

```
'You are Nikhil.'
```

To reset conversation_history:

```python
MB.reset_conversation_history()
```

## Using it yourself

The code should work out of the box, provided:
- you have the right packages installed 
- you have a file called `api_key.py` inside the `src` folder. This file should contain a variable called `open_ai_key` which has your Open AI key as a string. 