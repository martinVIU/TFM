#!/usr/bin/env python
# coding: utf-8

# In[1]:


from PIL import Image
import ollama


# In[2]:


def generate_text(instruction, file_path):
    result = ollama.generate(
        model='llava',
        prompt=instruction,
        images=[file_path],
        stream=False
    )['response']
    img=Image.open(file_path, mode='r')
    img = img.resize([int(i/1.2) for i in img.size])
    display(img) 
    for i in result.split('.'):
        print(i, end='', flush=True)


# In[3]:


instruction = "I want to upload this picture on instagram, I need caption ideas that will make me look badass"
file_path = 'tiburon.jpg'
generate_text(instruction, file_path)


# In[ ]:




