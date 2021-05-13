# Snake game done in Pygame

The video is a bit laggy - it's not a feature of the game!

https://user-images.githubusercontent.com/50328147/118126895-3c032600-b3f9-11eb-8b04-bf3b5cefa825.mp4

Art and music made by me.
Death sound and the the sound of getting an apple were made using: https://sfxr.me/

----------

I'm not very proud of how the code is laid out - it's very messy. I tried to divide it into more files but I failed miserably - it became even more messier than before. In the end most of the code is located in single file (main.py)  

When it comes to how the snake is represented as two classess: SnakeHead and SnakePart - I'm not very pleased with that. I should have made a parent class from which children like SnakeHead, SnakeTorso and SnakeTail could inherit. Also the connection of every snake part like a linked list with previous and next element could be replaced with an array representation - looping through a list of parts should more readable than propagating some function from part to part.

While Snake is generally a pretty easy game to make, the need to change images depending on the orientation of the body part makes everything much more complicated. 

  
**BUG WARNING!**  
If you change directions too quickly it's possible to do a 180 degree turn during one frame which results in collsion with yourself and death.
